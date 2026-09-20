[CmdletBinding()]
param(
    [string]$Python = "python",
    [string]$ReplayManifest = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-ReleasePython {
    param([string[]]$Arguments)
    & $Python -X utf8 @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python step failed (exit $LASTEXITCODE): $($Arguments -join ' ')"
    }
}

$repositoryPath = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repositoryPath
try {
    Invoke-ReleasePython -Arguments @("-m", "PyInstaller", "--version")
    Invoke-ReleasePython -Arguments @("-m", "release.ValidateRelease", "--inputs-only")
    $resolvedManifest = if ($ReplayManifest) { (Resolve-Path -LiteralPath $ReplayManifest).ProviderPath } else { "" }

    Invoke-ReleasePython -Arguments @("-m", "release.GeneratorGenerator")
    Invoke-ReleasePython -Arguments @("-m", "release.EquipmentTypeGenerator")
    Invoke-ReleasePython -Arguments @("-m", "release.JsonGenerator")
    Invoke-ReleasePython -Arguments @(
        "-m", "release.NameGenerator", "--resources", "equip/resources/cangshengtf",
        "--output", "replayer/NameCangsheng.py"
    )

    # A failed build or validation never replaces the previous published EXE.
    $stagingPath = Join-Path $repositoryPath ("build/release-" + [Guid]::NewGuid().ToString("N"))
    $candidatePath = Join-Path $stagingPath "MainWindow.exe"
    Invoke-ReleasePython -Arguments @(
        "-m", "PyInstaller", "--clean", "--noconfirm",
        "--distpath", $stagingPath, "--workpath", "build/standard-release",
        "MainWindow.spec"
    )
    Invoke-ReleasePython -Arguments @("-m", "release.ValidateRelease", "--exe", $candidatePath)

    $smokeDirectory = Join-Path $stagingPath "smoke"
    New-Item -ItemType Directory -Path $smokeDirectory | Out-Null
    # Keep generated icons and frozen resource lookup in the same fresh folder.
    $smokeExecutable = Join-Path $smokeDirectory "MainWindow.exe"
    Copy-Item -LiteralPath $candidatePath -Destination $smokeExecutable
    $smokeReport = Join-Path $smokeDirectory "release-smoke.json"
    $smokeArguments = @("--release-smoke-test", "--report", $smokeReport)
    if ($resolvedManifest) { $smokeArguments += @("--manifest", $resolvedManifest) }
    Push-Location -LiteralPath $smokeDirectory
    try {
        & $smokeExecutable @smokeArguments
        if ($LASTEXITCODE -ne 0) { throw "Release smoke test failed (exit $LASTEXITCODE)." }
        $smokeResult = Get-Content -LiteralPath $smokeReport -Raw | ConvertFrom-Json
        if ($smokeResult.status -ne "passed" -or -not $smokeResult.frozen) {
            throw "Release smoke test did not verify the frozen executable."
        }
    }
    finally {
        Pop-Location
    }

    $publishDirectory = Join-Path $repositoryPath "dist"
    New-Item -ItemType Directory -Path $publishDirectory -Force | Out-Null
    $publishPath = Join-Path $publishDirectory "j3jz.exe"
    Move-Item -LiteralPath $candidatePath -Destination $publishPath -Force
    $artifactHash = (Get-FileHash -LiteralPath $publishPath -Algorithm SHA256).Hash
    Write-Host "Build and resource verification completed: $publishPath"
    Write-Host "SHA256: $artifactHash"
    Write-Host "Smoke report: $smokeReport"
    Write-Host "Review and test the artifact before committing, pushing, or publishing a download link."
}
finally {
    Pop-Location
}
