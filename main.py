import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text

from app.api.routes.reports import router as reports_router
from app.core.config import settings
from app.database import Base, engine
from app.models import AuditLog, Report, User  # noqa: F401

logger = logging.getLogger("civicguard")

DASHBOARD = Path(__file__).resolve().parent / "dashboard" / "index.html"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        logger.exception("Could not initialize database tables")
    yield


app = FastAPI(
    title="CivicGuard",
    description="Civic incident reporting platform for India",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router)


@app.get("/health")
def health() -> dict[str, str]:
    database = "ok"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database = "unavailable"
    return {"status": "ok", "service": "CivicGuard", "database": database}


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(DASHBOARD)
