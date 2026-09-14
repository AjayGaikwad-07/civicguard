from fastapi import FastAPI

from app.api.routes.reports import router as reports_router

app = FastAPI(
    title="CivicGuard",
    description="Civic incident reporting platform for India",
    version="0.2.0",
)

app.include_router(reports_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "CivicGuard"}
