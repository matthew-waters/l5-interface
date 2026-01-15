#!/usr/bin/env bash
set -euo pipefail

# Run the Textual app via the Textual CLI in dev mode.
# Usage: ./scripts/run_textual_dev.sh

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

textual run --dev src.ui.app:L5InterfaceApp

