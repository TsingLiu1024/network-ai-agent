[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param([switch]$Execute)
$ErrorActionPreference = 'Stop'
if (-not $Execute) { throw 'This script requires -Execute; may disconnect network sessions and require reboot.' }
if ($env:OS -ne 'Windows_NT') { throw 'Windows is required.' }
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Administrator privileges are required.' }
if ($PSCmdlet.ShouldProcess('Local Windows network stack', 'Reset Winsock; may disrupt networking, save work and record configuration first')) {
    & netsh winsock reset
    if ($LASTEXITCODE -ne 0) { throw "Winsock reset failed (exit $LASTEXITCODE)." }
    Write-Output 'Reset completed; restart only after saving work. Verify connectivity after restart.'
}
