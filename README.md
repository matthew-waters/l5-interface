# l5-interface

Textual-based CLI interface for the carbon-, application-, and availability-aware scheduling system.

This repository is currently scaffold-only (file structure and placeholders).

## Running

- **Normal run** (no dev hot-reload):
  - `python -m src`
  - Or: `./scripts/run_python.sh` / `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_python.ps1`

- **Textual run** (Textual CLI):
  - `textual run src.app:L5InterfaceApp`
  - Or: `./scripts/run_textual.sh` / `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_textual.ps1`

- **Dev mode** (Textual CLI with dev features):
  - `textual run --dev src.app:L5InterfaceApp`
  - Or: `./scripts/run_textual_dev.sh` / `powershell -ExecutionPolicy Bypass -File .\\scripts\\run_textual_dev.ps1`
