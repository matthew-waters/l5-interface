$ErrorActionPreference = "Stop"

<# 
Run the app via Python's module entrypoint.
Usage: powershell -ExecutionPolicy Bypass -File .\scripts\run_python.ps1
#>

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

python -m src

