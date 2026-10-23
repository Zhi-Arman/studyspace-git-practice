#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
if [ ! -x backend/.venv/bin/python ]; then
  echo 'Run bash scripts/setup.sh first.' >&2; exit 1
fi
backend/.venv/bin/python scripts/check_docs.py
backend/.venv/bin/python scripts/generate_registers.py --check
backend/.venv/bin/python scripts/check_api_contract.py
uv run --directory backend --frozen ruff check app tests ../scripts ../tests
uv run --directory backend --frozen ruff format --check app tests ../scripts ../tests
uv run --directory backend --frozen pytest tests ../tests -q
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test
npm --prefix frontend run build
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  docker compose config --quiet
else
  echo 'SKIP: optional Docker Compose configuration check (CLI unavailable).'
fi
echo 'All scaffold checks passed / 骨架检查通过 / Проверки каркаса пройдены.'
