import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def clean_configuration(monkeypatch):
    # Never use the developer's real credentials/endpoints in offline tests.
    for name in (
        "MODEL_PROVIDER",
        "LLM_PROVIDER",
        "OLLAMA_HOST",
        "OLLAMA_URL",
        "OLLAMA_MODEL",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
