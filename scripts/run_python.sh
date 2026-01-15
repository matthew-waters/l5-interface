#!/usr/bin/env bash
set -euo pipefail

# Run the app via Python's module entrypoint.
# Usage: ./scripts/run_python.sh

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python -m src

