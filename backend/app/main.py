"""Local reservation API, offline reference and optional packaged frontend."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from html import escape
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from app import __version__
from app.admin import router as admin_router
from app.api import router as account_router
from app.config import PROJECT_DIR, Settings
from app.database import create_db_engine, create_session_factory, get_engine
from app.errors import AppError
from app.maintenance import daily_maintenance, seed_demo
from app.migration import migrate
from app.reservations_api import router as reservations_router


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["StudySpace"] = "StudySpace"
    version: str = __version__


class ReadyResponse(HealthResponse):
    database: Literal["ok"] = "ok"


class UnavailableResponse(BaseModel):
    status: Literal["unavailable"] = "unavailable"
    service: Literal["StudySpace"] = "StudySpace"
    version: str = __version__
    database: Literal["unavailable"] = "unavailable"


def create_app(
    settings: Settings | None = None,
    engine: Engine | None = None,
    static_dir: Path | None = None,
) -> FastAPI:
    settings = settings if settings is not None else Settings()
    db_engine = engine if engine is not None else create_db_engine(settings)

    async def maintain() -> None:
        while True:
            try:
                await asyncio.to_thread(daily_maintenance, db_engine)
            except Exception:
                logging.getLogger(__name__).error("Local maintenance failed; check data directory.")
            await asyncio.sleep(3600)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        maintenance = None
        try:
            migrate(db_engine)
            if settings.seed_demo and settings.app_env != "test":
                seed_demo(db_engine)
            if settings.app_env != "test" and db_engine.dialect.name == "sqlite":
                maintenance = asyncio.create_task(maintain())
            yield
        finally:
            if maintenance is not None:
                maintenance.cancel()
                with suppress(asyncio.CancelledError):
                    await maintenance
            db_engine.dispose()

    application = FastAPI(
        title="StudySpace API",
        version=__version__,
        description="Local-only StudySpace accounts, seats, reservations and administration.",
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan,
    )
    application.state.settings = settings
    application.state.engine = db_engine
    application.state.session_factory = create_session_factory(db_engine)
    application.include_router(account_router)
    application.include_router(reservations_router)
    application.include_router(admin_router)

    @application.exception_handler(AppError)
    async def app_error(_request, error: AppError):
        return JSONResponse(
            status_code=error.status,
            content={"error": {"code": error.code, "message": error.message}},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error(_request, error: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Check the submitted fields.",
                    "fields": [".".join(map(str, item["loc"])) for item in error.errors()],
                }
            },
        )

    @application.middleware("http")
    async def same_origin_writes(request, call_next):
        if request.url.path.startswith("/api/") and request.method in {
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }:
            origin = request.headers.get("origin")
            if request.headers.get("x-studyspace-request") != "1" or (
                origin is not None and origin not in settings.cors_origins
            ):
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": {
                            "code": "CROSS_SITE_REQUEST",
                            "message": "Use the local application to submit.",
                        }
                    },
                )
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-StudySpace-Request"],
    )

    @application.get("/api/v1/health", response_model=HealthResponse, tags=["Operations"])
    def health() -> HealthResponse:
        """Process liveness; does not claim that business features or a database are ready."""
        return HealthResponse()

    @application.get(
        "/api/v1/ready",
        response_model=ReadyResponse,
        responses={503: {"model": UnavailableResponse}},
        tags=["Operations"],
    )
    def ready(
        database_engine: Annotated[Engine, Depends(get_engine)],
    ) -> ReadyResponse | JSONResponse:
        """Check a database connection after startup migrations."""
        try:
            with database_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            # Do not include database URLs, driver messages or filesystem paths in HTTP output.
            return JSONResponse(status_code=503, content=UnavailableResponse().model_dump())
        return ReadyResponse()

    @application.get("/api/v1/docs", response_class=HTMLResponse, include_in_schema=False)
    def reference():
        rows = []
        for path, methods in application.openapi()["paths"].items():
            for method, operation in methods.items():
                if method in {"get", "post", "put", "patch", "delete"}:
                    rows.append(
                        f"<tr><td>{method.upper()}</td><td><code>{escape(path)}</code></td>"
                        f"<td>{escape(operation.get('summary', ''))}</td></tr>"
                    )
        return (
            """<!doctype html><html lang="en"><meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>StudySpace local API</title><style>
        body{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:1rem;background:#faf8f3}
        td,th{padding:.7rem;text-align:left;border-bottom:1px solid #ddd}
        code{overflow-wrap:anywhere}
        table{width:100%}a{color:#245b47}</style><h1>StudySpace local API</h1>
        <p>Offline endpoint reference. Local accounts only; HttpOnly session cookie.
        Writes require X-StudySpace-Request: 1 and an allowed Origin.</p>
        <p><a href="/api/v1/openapi.json">OpenAPI JSON: request schemas and parameters</a></p>
        <table><tr><th>Method</th><th>Path</th><th>Summary</th></tr>"""
            + "".join(rows)
            + "</table></html>"
        )

    build = (static_dir or PROJECT_DIR / "frontend" / "dist").resolve()
    if (build / "index.html").is_file():

        @application.get("/{path:path}", include_in_schema=False)
        def frontend(path: str):
            target = (build / path).resolve()
            if path == "api" or path.startswith("api/") or not target.is_relative_to(build):
                raise HTTPException(404)
            if target.is_file():
                return FileResponse(target)
            if Path(path).suffix or path.startswith("assets/"):
                raise HTTPException(404)
            return FileResponse(build / "index.html")

    return application


app = create_app()
