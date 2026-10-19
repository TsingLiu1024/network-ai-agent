import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient

import app as app_module
from config.settings import Settings


class Manager:
    def __init__(self, status="success"):
        self.status = status

    def prepare(self):
        pass

    def run(self, question):
        return {"status": self.status, "stages": {}, "evidence_scope": "api_server"}


def make_app(manager=None, **kwargs):
    config = Settings(_env_file=None, ENABLE_RAG=False, MODEL_PROVIDER="demo", **kwargs)
    return app_module.create_app(config, manager or Manager())


def test_documented_route_and_legacy_payload():
    with TestClient(make_app()) as client:
        result = client.post("/api/v1/diagnose", json={"question": "DNS failure"})
        assert result.status_code == 200
        assert result.json()["success"] is True
        assert result.headers["x-request-id"]
        assert client.post("/diagnose", json={"problem": "DNS failure"}).status_code == 200


@pytest.mark.parametrize("question", ["", "   ", "x" * 2001])
def test_empty_and_oversized_question_rejected(question):
    with TestClient(make_app()) as client:
        response = client.post("/api/v1/diagnose", json={"question": question})
        assert response.status_code == 422


def test_model_failure_and_partial_status_are_not_success():
    for status, code in [("failed", 502), ("partial", 200)]:
        with TestClient(make_app(Manager(status))) as client:
            response = client.post("/api/v1/diagnose", json={"question": "failure"})
            assert response.status_code == code
            assert response.json()["success"] is False
            assert response.json()["status"] == status


def test_authentication_and_large_body():
    with TestClient(make_app(API_KEY="test-key")) as client:
        assert client.post("/api/v1/diagnose", json={"question": "x"}).status_code == 401
        response = client.post(
            "/api/v1/diagnose", json={"question": "x"}, headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == 200
        assert client.post("/api/v1/diagnose", content=b"x" * 17000).status_code == 413


def test_internal_error_does_not_expose_details():
    class Broken(Manager):
        def run(self, question):
            raise RuntimeError("secret private path")

    with TestClient(make_app(Broken()), raise_server_exceptions=False) as client:
        response = client.post("/api/v1/diagnose", json={"question": "x"})
        assert response.status_code == 500
        assert "secret" not in response.text


def test_model_output_does_not_return_obvious_credentials():
    class Echo(Manager):
        def run(self, question):
            result = super().run(question)
            result["stages"] = {"answer": "api_key=confidential"}
            return result

    with TestClient(make_app(Echo())) as client:
        response = client.post("/api/v1/diagnose", json={"question": "x"})
        assert "confidential" not in response.text


def test_credentials_in_question_and_validation_input_are_not_echoed():
    with TestClient(make_app()) as client:
        success = client.post("/api/v1/diagnose", json={"question": "api_key=confidential"})
        assert "confidential" not in success.text
        invalid = client.post(
            "/api/v1/diagnose", json={"question": "api_key=confidential", "extra": "private"}
        )
        assert invalid.status_code == 422
        assert "confidential" not in invalid.text
        assert "private" not in invalid.text


def test_late_worker_failure_after_cancellation_is_observed():
    started, release, finished = threading.Event(), threading.Event(), threading.Event()

    class LateFailure(Manager):
        def run(self, question):
            started.set()
            release.wait(3)
            finished.set()
            raise RuntimeError("private upstream failure")

    app = make_app(LateFailure(), MAX_CONCURRENT_DIAGNOSES=1)
    errors = []

    async def scenario():
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(lambda _, context: errors.append(context))
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                task = asyncio.create_task(client.post("/api/v1/diagnose", json={"question": "x"}))
                assert await asyncio.to_thread(started.wait, 1)
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
                release.set()
                assert await asyncio.to_thread(finished.wait, 1)
                await asyncio.sleep(0.05)

    asyncio.run(scenario())
    assert errors == []


def test_real_pipeline_provider_outage_produces_502(monkeypatch):
    import requests

    def unavailable(*args, **kwargs):
        raise requests.ConnectionError("private credentials must not escape")

    monkeypatch.setattr(requests, "post", unavailable)
    config = Settings(_env_file=None, MODEL_PROVIDER="ollama", ENABLE_RAG=False)
    with TestClient(app_module.create_app(config)) as client:
        response = client.post("/api/v1/diagnose", json={"question": "failure"})
        assert response.status_code == 502
        body = response.json()
        assert body["status"] == "failed"
        assert body["result"]["stages"]["repair"]["success"] is False
        assert "private credentials" not in response.text


def test_real_demo_pipeline_needs_no_model_or_local_evidence(monkeypatch):
    def forbidden(*a, **k):
        pytest.fail("Offline demo touched an external dependency")

    monkeypatch.setattr("requests.post", forbidden)
    monkeypatch.setattr("subprocess.run", forbidden)
    config = Settings(_env_file=None, MODEL_PROVIDER="demo", ENABLE_RAG=False)
    with TestClient(app_module.create_app(config)) as client:
        assert client.get("/ready").json()["rag"] == "disabled"
        response = client.post("/api/v1/diagnose", json={"question": "failure"})
        assert response.json()["status"] == "demo"
        assert response.json()["result"]["execution_enabled"] is False


def test_http_timeout_retains_capacity_until_worker_finishes():
    started, release = threading.Event(), threading.Event()

    class Slow(Manager):
        def run(self, question):
            started.set()
            release.wait(3)
            return super().run(question)

    with TestClient(make_app(Slow(), MAX_CONCURRENT_DIAGNOSES=1, DIAGNOSIS_TIMEOUT=0.02)) as client:
        try:
            response = client.post("/api/v1/diagnose", json={"question": "x"})
            assert response.status_code == 504
            assert started.is_set()
            assert client.post("/api/v1/diagnose", json={"question": "y"}).status_code == 503
        finally:
            release.set()


def test_shutdown_drains_active_workers_before_releasing_resources():
    release = threading.Event()

    class Slow(Manager):
        def run(self, question):
            release.wait(3)
            return super().run(question)

    app = make_app(Slow(), DIAGNOSIS_TIMEOUT=0.01)

    async def scenario():
        lifespan = app.router.lifespan_context(app)
        await lifespan.__aenter__()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            assert (
                await client.post("/api/v1/diagnose", json={"question": "x"})
            ).status_code == 504
        closing = asyncio.create_task(lifespan.__aexit__(None, None, None))
        try:
            await asyncio.sleep(0.05)
            assert not closing.done()
        finally:
            release.set()
            await closing

    asyncio.run(scenario())


def test_busy_worker_does_not_block_health_and_capacity_recovers():
    started, release = threading.Event(), threading.Event()

    class Slow(Manager):
        def run(self, question):
            started.set()
            release.wait(3)
            return super().run(question)

    app = make_app(Slow(), MAX_CONCURRENT_DIAGNOSES=1)
    with TestClient(app) as client, ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(client.post, "/api/v1/diagnose", json={"question": "x"})
        assert started.wait(1)
        try:
            assert client.get("/health").status_code == 200
            assert client.post("/api/v1/diagnose", json={"question": "y"}).status_code == 503
        finally:
            release.set()
        assert pending.result().status_code == 200
        assert client.post("/api/v1/diagnose", json={"question": "z"}).status_code == 200


def test_cancelled_request_retains_slot_until_actual_worker_finishes():
    started, release = threading.Event(), threading.Event()

    class Slow(Manager):
        def run(self, question):
            started.set()
            release.wait(3)
            return super().run(question)

    app = make_app(Slow(), MAX_CONCURRENT_DIAGNOSES=1)

    async def scenario():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                task = asyncio.create_task(client.post("/api/v1/diagnose", json={"question": "x"}))
                await asyncio.to_thread(started.wait, 1)
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
                try:
                    assert (
                        await client.post("/api/v1/diagnose", json={"question": "y"})
                    ).status_code == 503
                finally:
                    release.set()

    asyncio.run(scenario())
