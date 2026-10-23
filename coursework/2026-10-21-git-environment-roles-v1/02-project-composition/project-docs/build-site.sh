#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p artifacts
DOCS_PYTHON="${DOCS_PYTHON:-.venv/bin/python}"
"$DOCS_PYTHON" -m sphinx -b html -n -W --keep-going -E -a -N \
  -w artifacts/sphinx-warnings.log docs site 2>&1 | tee artifacts/sphinx-build.log
