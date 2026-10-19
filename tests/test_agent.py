import json
from types import SimpleNamespace

import pytest

from agents.log_agent import LogAgent
from agents.network_agent import NetworkAgent
from agents.repair_agent import RepairAgent
from config.settings import Settings
from llm.base import LLMError


def test_network_agent_returns_actual_probe_evidence(monkeypatch):
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="real fixture", stderr=""),
    )
    result = NetworkAgent().run("network failure")
    assert result.success
    assert result.data["ping"]["output"] == "real fixture"


def test_cloud_logs_are_not_collected_without_opt_in(monkeypatch):
    def forbidden(*a, **k):
        pytest.fail("private log collection was attempted")

    monkeypatch.setattr("subprocess.run", forbidden)
    result = LogAgent(
        Settings(_env_file=None, MODEL_PROVIDER="deepseek", COLLECT_LOCAL_EVIDENCE=True)
    ).run("failure")
    assert not result.success
    assert result.metadata["status"] == "skipped"


def test_log_collection_failure_remains_failure(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr="private data"),
    )
    result = LogAgent(Settings(_env_file=None, COLLECT_LOCAL_EVIDENCE=True)).run("failure")
    assert not result.success
    assert "private data" not in str(result.to_dict())


@pytest.mark.parametrize("raw", ["not json", '{"reason":"x","steps":[],"commands":"x"}', "{}"])
def test_invalid_repair_plan_is_rejected(raw):
    class Model:
        def chat(self, prompt, timeout=None):
            return raw

    result = RepairAgent(llm=Model()).run("failure")
    assert not result.success
    assert result.metadata["error_code"] == "invalid_repair_plan"


def test_valid_repair_plan_is_typed_and_suggestion_only():
    class Model:
        def chat(self, prompt, timeout=None):
            return json.dumps(
                {
                    "reason": "DNS issue suspected",
                    "steps": ["Run lookup first"],
                    "commands": [
                        {
                            "command": "nslookup github.com",
                            "description": "Check DNS",
                            "platform": "windows",
                            "requires_admin": False,
                            "risk": "read_only",
                            "verification": "Review returned addresses",
                        }
                    ],
                }
            )

    result = RepairAgent(llm=Model()).run("failure")
    assert result.success
    assert result.data["repair_plan"]["commands"][0]["risk"] == "read_only"
    assert result.data["execution_enabled"] is False


def test_provider_error_does_not_become_successful_repair():
    class Model:
        def chat(self, prompt, timeout=None):
            raise LLMError("provider_unavailable", "Model unavailable")

    result = RepairAgent(llm=Model()).run("failure")
    assert not result.success
    assert result.metadata["error_code"] == "provider_unavailable"
