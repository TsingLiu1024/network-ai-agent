"""API creation is side-effect free: no models, host probes or index loads."""

import asyncio
import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from agents.core.manager import AgentManager
from api import router
from api.errors import global_exception_handler, validation_exception_handler
from config.settings import settings

logger = logging.getLogger(__name__)


class BodyLimitMiddleware:
    def __init__(self, app, limit=16000):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        try:
            async with asyncio.timeout(5):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    data = message.get("body", b"")
                    size += len(data)
                    if size > self.limit:
                        return await JSONResponse(
                            {"success": False, "error": "Request too large"}, status_code=413
                        )(scope, receive, send)
                    chunks.append(data)
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            return await JSONResponse(
                {"success": False, "error": "Request body timeout"}, status_code=408
            )(scope, receive, send)
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()

        return await self.app(scope, replay, send)


def create_app(config=None, manager=None):
    config = config or settings

    @asynccontextmanager
    async def lifespan(app):
        # Preparation may load local embeddings; it never blocks the ASGI loop.
        app.state.agent_manager = manager or AgentManager(config)
        await asyncio.to_thread(app.state.agent_manager.prepare)
        app.state.executor = ThreadPoolExecutor(
            max_workers=config.MAX_CONCURRENT_DIAGNOSES, thread_name_prefix="diagnosis"
        )
        app.state.slots = threading.BoundedSemaphore(config.MAX_CONCURRENT_DIAGNOSES)
        app.state.ready = True
        try:
            yield
        finally:
            app.state.ready = False
            await asyncio.to_thread(app.state.executor.shutdown, wait=True, cancel_futures=True)

    app = FastAPI(title="Network AI Agent", version="2.1.0", lifespan=lifespan)
    app.state.config = config
    app.state.ready = False
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_middleware(BodyLimitMiddleware)

    @app.middleware("http")
    async def trace_request(request: Request, call_next):
        # Do not trust user-controlled IDs in logs.
        request.state.request_id = uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(router)

    @app.get("/")
    def root():
        return {"name": "Network AI Agent", "version": "2.1.0", "execution_enabled": False}

    @app.get("/health")
    async def health():
        return {"status": "alive"}

    @app.get("/ready")
    async def ready():
        if not app.state.ready:
            return JSONResponse({"status": "not_ready"}, status_code=503)
        agents = getattr(app.state.agent_manager, "agents", {})
        rag = agents.get("rag")
        return {
            "status": "ready",
            "rag": "disabled"
            if not config.ENABLE_RAG
            else "ready"
            if rag and rag.ready
            else "degraded",
            "scope": "api_server",
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000)
