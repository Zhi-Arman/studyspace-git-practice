"""The packaged local server serves only build assets and keeps API 404s as JSON."""

from app.main import create_app
from fastapi.testclient import TestClient


def test_local_static_build_and_api_routes_remain_separate(engine, tmp_path):
    assets = tmp_path / "frontend"
    (assets / "assets").mkdir(parents=True)
    (assets / "index.html").write_text("<html><h1>StudySpace local build</h1></html>")
    (assets / "assets/test.js").write_text("console.log('local')")
    from app.config import Settings

    settings = Settings(_env_file=None, app_env="test", database_url=str(engine.url))
    application = create_app(settings, engine, static_dir=assets)
    with TestClient(application) as client:
        assert "StudySpace local build" in client.get("/").text
        assert client.get("/my-bookings").status_code == 200
        assert client.get("/assets/test.js").headers["content-type"].startswith("text/javascript")
        missing = client.get("/api/v1/does-not-exist")
        assert missing.status_code == 404
        assert missing.headers["content-type"].startswith("application/json")
        assert client.get("/assets/missing.js").status_code == 404
        assert client.get("/%2e%2e/backend/data/studyspace.db").status_code == 404
        docs = client.get("/api/v1/docs")
        assert docs.status_code == 200
        assert "cdn.jsdelivr.net" not in docs.text
        assert "https://" not in docs.text
