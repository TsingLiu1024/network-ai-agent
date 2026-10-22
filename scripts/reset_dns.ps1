[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param([switch]$Execute)
$ErrorActionPreference = 'Stop'
if (-not $Execute) { throw 'This script requires -Execute; review the operation first.' }
if ($env:OS -ne 'Windows_NT') { throw 'Windows is required.' }
if ($PSCmdlet.ShouldProcess('Local Windows DNS cache', 'Clear cache; does not reset network settings')) {
    & ipconfig /flushdns
    if ($LASTEXITCODE -ne 0) { throw "DNS cache clear failed (exit $LASTEXITCODE)." }
}
