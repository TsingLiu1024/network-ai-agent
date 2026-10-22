import json

import pytest
import requests

from config.settings import Settings
from llm.factory import get_llm


def test_documented_provider_controls_actual_client(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only")
    config = Settings(_env_file=None)
    client = get_llm(config)
    assert client.name == "deepseek"


def test_legacy_provider_alias_and_endpoint_alias(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_HOST", "http://example.invalid:11434")
    config = Settings(_env_file=None)
    client = get_llm(config)
    assert client.host == "http://example.invalid:11434"
    assert client.model == config.OLLAMA_MODEL


def test_environment_alias_overrides_dotenv_defaults(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text("MODEL_PROVIDER=ollama\nOLLAMA_URL=http://dotenv.invalid\n")
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("OLLAMA_HOST", "http://environment.invalid")
    config = Settings(_env_file=dotenv)
    assert config.MODEL_PROVIDER == "deepseek"
    assert config.OLLAMA_URL == "http://environment.invalid"


@pytest.mark.parametrize("provider", ["ollama", "deepseek", "openai"])
def test_all_providers_use_config_and_bounded_http(provider, monkeypatch):
    config = Settings(
        _env_file=None,
        MODEL_PROVIDER=provider,
        OPENAI_API_KEY="test-only",
        DEEPSEEK_API_KEY="test-only",
        OPENAI_MODEL="custom-open",
        DEEPSEEK_MODEL="custom-deep",
        OLLAMA_MODEL="custom-local",
        OPENAI_BASE_URL="http://api.invalid/v1",
        DEEPSEEK_BASE_URL="http://api.invalid/v1",
    )
    calls = []

    class Response:
        status_code = 200

        def json(self):
            return {"response": "valid", "choices": [{"message": {"content": "valid"}}]}

        def iter_content(self, chunk_size):
            yield json.dumps(self.json()).encode()

        def close(self):
            pass

    def post(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(requests, "post", post)
    client = get_llm(config)
    assert client.chat("hello", timeout=2) == "valid"
    url, args = calls[0]
    expected = {"ollama": "custom-local", "deepseek": "custom-deep", "openai": "custom-open"}
    assert args["json"]["model"] == expected[provider]
    assert 0 < args["timeout"] <= 2
    if provider != "ollama":
        assert url == "http://api.invalid/v1/chat/completions"


@pytest.mark.parametrize("kind", ["connection", "unauthorized", "empty", "malformed", "oversize"])
def test_llm_failures_raise_safe_error(kind, monkeypatch):
    from llm.base import LLMError

    client = get_llm(Settings(_env_file=None, MODEL_PROVIDER="ollama", MAX_LLM_OUTPUT_CHARS=100))

    class Response:
        status_code = 401 if kind == "unauthorized" else 200

        def json(self):
            if kind == "malformed":
                raise ValueError("private response")
            return {"response": "x" * 101 if kind == "oversize" else ""}

        def iter_content(self, chunk_size):
            yield json.dumps(self.json()).encode()

        def close(self):
            pass

    def post(*args, **kwargs):
        if kind == "connection":
            raise requests.ConnectionError("secret-token private-host")
        return Response()

    monkeypatch.setattr(requests, "post", post)
    with pytest.raises(LLMError) as caught:
        client.chat("hello")
    assert "secret-token" not in str(caught.value)
    assert "private" not in str(caught.value)


def test_prompt_has_total_limit(monkeypatch):
    from llm.base import LLMError

    client = get_llm(Settings(_env_file=None, MAX_CONTEXT_LENGTH=100))
    with pytest.raises(LLMError):
        client.chat("x" * 101)


def test_invalid_provider_and_missing_credentials_fail_before_use():
    with pytest.raises(ValueError):
        Settings(_env_file=None, MODEL_PROVIDER="unknown")
    with pytest.raises(ValueError):
        get_llm(Settings(_env_file=None, MODEL_PROVIDER="openai"))


def test_oversized_http_response_stops_before_reading_entire_body(monkeypatch):
    from llm.base import LLMError

    consumed, closed = [], []

    class Response:
        status_code = 200

        def json(self):
            raise AssertionError("unbounded JSON read")

        def iter_content(self, chunk_size):
            for _ in range(100):
                consumed.append(1)
                yield b"x" * 4096

        def close(self):
            closed.append(True)

    monkeypatch.setattr(requests, "post", lambda *a, **k: Response())
    client = get_llm(Settings(_env_file=None, MAX_LLM_OUTPUT_CHARS=100))
    with pytest.raises(LLMError):
        client.chat("hello")
    assert len(consumed) < 100
    assert closed
