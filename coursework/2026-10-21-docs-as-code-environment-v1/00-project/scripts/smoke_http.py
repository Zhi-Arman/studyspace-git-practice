#!/usr/bin/env python3
"""Read-only HTTP smoke checks; run while bash scripts/dev.sh is running."""

import json
import urllib.request


def read(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(f"{url}: HTTP {response.status}")
        return response.read()


def main() -> int:
    expected = {"status": "ok", "service": "StudySpace", "version": "0.1.0"}
    for origin in ("http://127.0.0.1:8000", "http://127.0.0.1:5173"):
        health = json.loads(read(f"{origin}/api/v1/health"))
        if health != expected:
            raise RuntimeError(f"{origin}: health contract differs")
        ready = json.loads(read(f"{origin}/api/v1/ready"))
        if ready != {**expected, "database": "ok"}:
            raise RuntimeError(f"{origin}: database not ready")
        schema = json.loads(read(f"{origin}/api/v1/openapi.json"))
        if set(schema["paths"]) != {"/api/v1/health", "/api/v1/ready"}:
            raise RuntimeError(f"{origin}: unexpected foundation endpoints")
        if b"swagger-ui" not in read(f"{origin}/api/v1/docs"):
            raise RuntimeError(f"{origin}: Swagger HTML missing")
        print(f"PASS: {origin} health, SQLite readiness, OpenAPI and Swagger HTML")
    if b"StudySpace" not in read("http://127.0.0.1:5173/"):
        raise RuntimeError("Frontend index HTML missing StudySpace")
    print("PASS: frontend index HTML served; rendering is checked separately in a browser")
    print("No business features or user acceptance are claimed by these checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
