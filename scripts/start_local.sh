#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
port="${STUDYSPACE_PORT:-8000}"
if ! [[ "$port" =~ ^[0-9]+$ ]] || (( port < 1024 || port > 65535 )); then
  echo 'STUDYSPACE_PORT must be 1024–65535.' >&2; exit 1
fi
[ -x backend/.venv/bin/python ] || { echo 'Run bash scripts/setup.sh first.' >&2; exit 1; }
npm --prefix frontend run build
export CORS_ORIGINS="[\"http://127.0.0.1:$port\",\"http://localhost:$port\"]"
cd backend
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "$port"
