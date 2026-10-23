#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
if [ ! -x backend/.venv/bin/python ] || [ ! -d frontend/node_modules ]; then
  echo 'Run bash scripts/setup.sh first / 请先安装依赖 / Сначала установите зависимости.' >&2
  exit 1
fi
# Check fixed development ports before starting either service.
backend/.venv/bin/python - <<'PY'
import socket
for port in (8000, 5173):
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            raise SystemExit(f"Port {port} unavailable; stop its owner before starting StudySpace.")
PY
cleanup() {
  trap - EXIT INT TERM
  if [ -n "${backend_pid:-}" ]; then kill "$backend_pid" 2>/dev/null || true; fi
  if [ -n "${frontend_pid:-}" ]; then kill "$frontend_pid" 2>/dev/null || true; fi
  wait 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 &
backend_pid=$!
# Launch Vite directly so cleanup owns its actual process, without an npm wrapper.
(cd frontend && exec node node_modules/vite/bin/vite.js) &
frontend_pid=$!
echo 'StudySpace: http://127.0.0.1:5173 | API: http://127.0.0.1:8000/api/v1/docs | Ctrl+C stops both.'
while kill -0 "$backend_pid" 2>/dev/null && kill -0 "$frontend_pid" 2>/dev/null; do
  sleep 1
done
echo 'A development service exited; shutting down the other service.' >&2
exit 1
