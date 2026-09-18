from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import router
from app.database import create_tables


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources during startup."""
    create_tables()
    yield


app = FastAPI(
    title="MiniKanban API",
    description="A lightweight Kanban task management API.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the Kanban frontend."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health_check():
    """Check whether the API is healthy."""
    return {"status": "healthy"}