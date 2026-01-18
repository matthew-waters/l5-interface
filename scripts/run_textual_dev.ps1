$ErrorActionPreference = "Stop"

<# 
Run the Textual app via the Textual CLI in dev mode.
Usage: powershell -ExecutionPolicy Bypass -File .\scripts\run_textual_dev.ps1
#>

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

textual run --dev src.app:L5InterfaceApp

