[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param([switch]$Execute)
$ErrorActionPreference = 'Stop'
if (-not $Execute) { throw 'This script requires -Execute; stops all running WSL distributions and processes.' }
if ($env:OS -ne 'Windows_NT') { throw 'Windows is required.' }
if ($PSCmdlet.ShouldProcess('All WSL distributions', 'Stop all processes; save work before proceeding')) {
    & wsl --shutdown
    if ($LASTEXITCODE -ne 0) { throw "WSL shutdown failed (exit $LASTEXITCODE)." }
    Write-Output 'WSL stopped. Start the required distribution and verify networking.'
}
