#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for tool in node npm uv; do
  command -v "$tool" >/dev/null || { echo "Missing tool / Нет инструмента: $tool" >&2; exit 1; }
done
node -e 'const [major, minor] = process.versions.node.split(".").map(Number); if (!(major === 22 && minor >= 13 || major >= 24)) { console.error("Node.js 22.13+ (22.x) or 24+ required"); process.exit(1); }'
cd "$project_root"
if [ ! -e .env ]; then cp .env.example .env; fi
uv sync --project backend --python "${STUDYSPACE_PYTHON:-3.13}" --frozen
npm --prefix frontend ci --no-audit --no-fund
echo 'Installed / 已安装 / Установлено. Run / 运行 / Запуск: bash scripts/dev.sh'
