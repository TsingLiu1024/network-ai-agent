import subprocess
from types import SimpleNamespace

import pytest

from tools.network import NetworkTool
from tools.powershell import PowerShellTool
from tools.wsl import WSLTool


@pytest.mark.parametrize("system,flag", [("Windows", "-n"), ("Linux", "-c")])
def test_network_uses_platform_flags_and_measured_results(monkeypatch, system, flag):
    monkeypatch.setattr("platform.system", lambda: system)
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=0, stdout="measured response", stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    result = NetworkTool().run()
    assert result.success
    assert result.data["ping"]["output"] == "measured response"
    assert result.data["scope"] == "api_server"
    assert flag in calls[0][0]
    assert all(c[1]["timeout"] > 0 and not c[1].get("shell") for c in calls)


def test_failed_probe_is_not_reported_as_success(monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr="private"),
    )
    result = NetworkTool().run()
    assert not result.success
    assert result.data["ping"]["success"] is False


def test_probe_timeout_is_visible(monkeypatch):
    def run(*args, **kwargs):
        raise subprocess.TimeoutExpired("probe", 1)

    monkeypatch.setattr(subprocess, "run", run)
    result = NetworkTool().run()
    assert not result.success
    assert result.data["dns"]["error"] == "timeout"


def test_invalid_target_rejected_without_process(monkeypatch):
    def forbidden(*a, **k):
        pytest.fail("invalid target reached subprocess")

    monkeypatch.setattr(subprocess, "run", forbidden)
    with pytest.raises(ValueError):
        NetworkTool().run("-help")


def test_arbitrary_shell_and_unconfirmed_repairs_are_blocked(monkeypatch):
    def forbidden(*a, **k):
        pytest.fail("unconfirmed repair executed")

    monkeypatch.setattr(subprocess, "run", forbidden)
    assert not PowerShellTool().run("Write-Output unexpected").success
    assert not PowerShellTool().run("flush_dns").success
    assert not WSLTool().run("restart").success


def test_confirmed_action_checks_exit_code(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=5, stdout="", stderr="denied")
    )
    assert not PowerShellTool().run("flush_dns", confirmed=True).success
    assert not WSLTool().run("restart", confirmed=True).success
