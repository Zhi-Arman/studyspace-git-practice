"""Health and readiness endpoints; no authentication or booking functionality."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from app import __version__
from app.api import router as account_router
from app.config import Settings
from app.database import create_db_engine, create_session_factory, get_engine
from app.errors import AppError
from app.migration import migrate


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


def create_app(settings: Settings | None = None, engine: Engine | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings()
    db_engine = engine if engine is not None else create_db_engine(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            migrate(db_engine)
            yield
        finally:
            db_engine.dispose()

    application = FastAPI(
        title="StudySpace API",
        version=__version__,
        description="Course project foundation. Business features are not implemented yet.",
        docs_url="/api/v1/docs",
        redoc_url=None,
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan,
    )
    application.state.settings = settings
    application.state.engine = db_engine
    application.state.session_factory = create_session_factory(db_engine)
    application.include_router(account_router)

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
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
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
        """Check a database connection without creating a domain schema."""
        try:
            with database_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            # Do not include database URLs, driver messages or filesystem paths in HTTP output.
            return JSONResponse(status_code=503, content=UnavailableResponse().model_dump())
        return ReadyResponse()

    return application


app = create_app()
