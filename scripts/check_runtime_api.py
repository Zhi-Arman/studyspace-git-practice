#!/usr/bin/env python3
"""Export/check the actual local API separately from the historical course example."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from openapi_spec_validator import validate  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    app = create_app(Settings(_env_file=None, app_env="test", database_url="sqlite:///:memory:"))
    schema = app.openapi()
    validate(schema)
    target = ROOT / "docs/api/local-openapi.json"
    serialized = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        target.write_text(serialized)
    if not target.is_file() or target.read_text() != serialized:
        raise SystemExit("Runtime OpenAPI is stale. Run check_runtime_api.py --write.")
    operations = sum(
        method in {"get", "post", "put", "patch", "delete"}
        for methods in schema["paths"].values()
        for method in methods
    )
    assert "/api/v1/bookings" in schema["paths"]
    assert "/api/v1/admin/users/{user_id}" in schema["paths"]
    assert "/api/v1/auth/register" in schema["paths"]
    print(f"Runtime OpenAPI valid and synchronized: {operations} operations.")
    app.state.engine.dispose()


if __name__ == "__main__":
    main()
