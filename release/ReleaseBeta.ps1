# Retained command entry; both builds now use the same level-50 formal data.
[CmdletBinding()]
param(
    [string]$Python = "python",
    [string]$ReplayManifest = "",
    [string]$WujieLog = ""
)

& (Join-Path $PSScriptRoot "Release.ps1") @PSBoundParameters
