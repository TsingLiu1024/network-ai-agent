import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("name", ["reset_dns.ps1", "reset_network.ps1", "repair_wsl.ps1"])
def test_reset_scripts_require_explicit_execute_flag(name):
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        pytest.skip("PowerShell unavailable")
    path = Path(__file__).resolve().parents[1] / "scripts" / name
    # Mask every original system command before exercising the script's entry point.
    # The baseline must fail this test without touching the real host.
    guard = "function global:netsh { throw 'unguarded system command' }; function global:ipconfig { throw 'unguarded system command' }; function global:wsl { throw 'unguarded system command' }; function global:net { throw 'unguarded system command' }; "
    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "$ErrorActionPreference='Stop'; " + guard + "& '" + str(path).replace("'", "''") + "'",
        ],
        capture_output=True,
        text=True,
        errors="replace",
        timeout=15,
    )
    assert result.returncode != 0
    assert "requires -Execute" in result.stderr
    assert "unguarded system command" not in result.stderr
