[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$Remote,

  [Parameter(Mandatory=$true)]
  [string]$RemoteDir,

  [Parameter(Mandatory=$true)]
  [string]$LocalDir,

  [Parameter(Mandatory=$true)]
  [string]$Cutoff,

  [int]$Port = 22,

  [ValidateSet('tar')]
  [string]$Mode = 'tar',

  [ValidateSet('none','gzip')]
  [string]$Compress = 'none',

  [switch]$DeleteRemote,

  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

function Require-Command([string]$Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Required command not found: $Name"
  }
}

Require-Command ssh
Require-Command tar

New-Item -ItemType Directory -Force -Path $LocalDir | Out-Null

# Remote find expression: files with mtime earlier than cutoff date
# Note: relies on GNU find on Linux remote.
$remoteFind = "find database/ActorStat database/ReplayProStat -type f ! -newermt '$Cutoff'"

if ($DryRun) {
  Write-Host "[Dry-run] Matched files (mtime < $Cutoff) count:"
  & ssh -p $Port $Remote "cd '$RemoteDir' && $remoteFind | wc -l"

  Write-Host "[Dry-run] Matched files total size (approx):"
  $bytesStr = (& ssh -p $Port $Remote "cd '$RemoteDir' && $remoteFind -printf '%s\n' 2>/dev/null | awk '{s+=`$1} END{print s}'").Trim()
  if ([string]::IsNullOrWhiteSpace($bytesStr)) {
    $bytesStr = '0'
  }
  $bytes = [int64]$bytesStr
  $gib = [math]::Round($bytes / 1GB, 3)
  Write-Host ("{0} bytes ({1} GiB)" -f $bytes, $gib)

  Write-Host "[Dry-run] Total directory sizes (NOT filtered; for reference):"
  & ssh -p $Port $Remote "cd '$RemoteDir' && du -sh database/ActorStat database/ReplayProStat 2>/dev/null || true"

  Write-Host "[Dry-run] Newer-than-cutoff files count (sanity check):"
  & ssh -p $Port $Remote "cd '$RemoteDir' && find database/ActorStat database/ReplayProStat -type f -newermt '$Cutoff' | wc -l"
  exit 0
}

if ($Mode -ne 'tar') {
  throw "Unsupported mode on PowerShell script: $Mode"
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$cutoffSafe = ($Cutoff -replace '[^0-9-]', '_')
$archiveName = if ($Compress -eq 'gzip') { "jx3bla-stat-$cutoffSafe-$timestamp.tar.gz" } else { "jx3bla-stat-$cutoffSafe-$timestamp.tar" }
$archivePath = Join-Path $LocalDir $archiveName

Write-Host "[1/3] Downloading archive to $archivePath (from ${Remote}:${RemoteDir}) ..."
# Download archive stream to a local file first, then verify/extract.
# This prevents accidental remote deletion when local extraction fails.
$remoteStreamCmd = "cd '$RemoteDir' && $remoteFind -print0 | tar --null -T - -cf -"
if ($Compress -eq 'gzip') {
  $remoteStreamCmd = $remoteStreamCmd + " | gzip -1"
}

& ssh -p $Port $Remote $remoteStreamCmd > $archivePath
if ($LASTEXITCODE -ne 0) {
  throw "ssh failed while downloading archive (exit=$LASTEXITCODE). Archive kept: $archivePath"
}

Write-Host "[2/3] Verifying archive format ..."
if ($Compress -eq 'gzip') {
  & tar -tzf $archivePath | Select-Object -First 1 | Out-Null
} else {
  & tar -tf $archivePath | Select-Object -First 1 | Out-Null
}
if ($LASTEXITCODE -ne 0) {
  throw "Local tar cannot read archive. This usually means the remote command output was not a tar stream (e.g., remote tar/find error, banner/MOTD on stdout). Archive kept: $archivePath"
}

Write-Host "[3/3] Extracting to $LocalDir ..."
if ($Compress -eq 'gzip') {
  & tar -xzf $archivePath -C $LocalDir
} else {
  & tar -xf $archivePath -C $LocalDir
}
if ($LASTEXITCODE -ne 0) {
  throw "Extraction failed (exit=$LASTEXITCODE). Remote NOT deleted. Archive kept: $archivePath"
}

if ($DeleteRemote) {
  Write-Host "Deleting matched files on remote (explicit -DeleteRemote) ..."
  & ssh -p $Port $Remote "cd '$RemoteDir' && $remoteFind -delete"
  if ($LASTEXITCODE -ne 0) {
    throw "Remote delete failed (exit=$LASTEXITCODE). Local backup exists at: $archivePath"
  }
  Write-Host "Done. Backup: $archivePath ; Extracted under: $LocalDir ; Remote deleted."
} else {
  Write-Host "Done. Backup: $archivePath ; Extracted under: $LocalDir ; Remote NOT deleted (use -DeleteRemote to delete)."
}