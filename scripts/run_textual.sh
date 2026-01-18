#!/usr/bin/env bash
set -euo pipefail

# Run the Textual app via the Textual CLI (non-dev mode).
# Usage: ./scripts/run_textual.sh

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

textual run src.app:L5InterfaceApp

