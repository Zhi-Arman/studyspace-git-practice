#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root/backend"
[ -x .venv/bin/python ] || { echo 'Run bash scripts/setup.sh first.' >&2; exit 1; }
exec .venv/bin/python -m app.cli "$@"
