$ErrorActionPreference = "Stop"

<# 
Run the Textual app via the Textual CLI (non-dev mode).
Usage: powershell -ExecutionPolicy Bypass -File .\scripts\run_textual.ps1
#>

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

textual run src.ui.app:L5InterfaceApp

