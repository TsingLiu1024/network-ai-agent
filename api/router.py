import asyncio
import hmac
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from llm.optimizer import redact, redact_data

from .schema import DiagnoseRequest, DiagnoseResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Diagnosis"])
api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


async def authenticate(request: Request, supplied: str | None = Depends(api_key)):
    expected = request.app.state.config.API_KEY
    if expected and not hmac.compare_digest(
        (supplied or "").encode(), expected.get_secret_value().encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.post(
    "/api/v1/diagnose", response_model=DiagnoseResponse, dependencies=[Depends(authenticate)]
)
@router.post(
    "/diagnose",
    response_model=DiagnoseResponse,
    include_in_schema=False,
    dependencies=[Depends(authenticate)],
)
async def diagnose(payload: DiagnoseRequest, request: Request):
    state = request.app.state
    slots = state.slots
    if not slots.acquire(blocking=False):
        raise HTTPException(
            status_code=503, detail="Diagnosis capacity reached", headers={"Retry-After": "5"}
        )
    try:
        future = state.executor.submit(state.agent_manager.run, payload.question)
    except Exception:
        slots.release()
        raise
    # Attach to the concurrent future, not an asyncio wrapper that may be cancelled.
    future.add_done_callback(lambda _: slots.release())
    try:
        result = await asyncio.wait_for(
            asyncio.shield(asyncio.wrap_future(future)), timeout=state.config.DIAGNOSIS_TIMEOUT
        )
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Diagnosis deadline exceeded") from None
    except Exception:
        logger.error("Diagnosis failed request_id=%s", request.state.request_id)
        raise HTTPException(status_code=500, detail="Diagnosis failed") from None
    result = redact_data(result)
    status = result["status"]
    body = DiagnoseResponse(
        success=status in {"success", "demo"},
        status=status,
        question=redact(payload.question),
        request_id=request.state.request_id,
        result=result,
    )
    return JSONResponse(status_code=502 if status == "failed" else 200, content=body.model_dump())
