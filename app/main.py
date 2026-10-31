"""Main FastAPI application entry point for Space Bounty Hunters REST API."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db, ping_db
from .routers import criminals, hunts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bounty_hunters")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events: initialize schema on startup."""
    logger.info("Initializing Space Bounty Hunters REST API...")
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as exc:
        logger.error("Failed to initialize database tables on startup: %s", exc)
    yield
    logger.info("Shutting down Space Bounty Hunters REST API.")


app = FastAPI(
    title="Space Bounty Hunters REST API",
    description=(
        "REST API for interplanetary bounty hunters. Provides access to galactic "
        "wanted criminal dossiers and a comprehensive journal of capture attempts."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for local testing and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(criminals.router)
app.include_router(hunts.router)


@app.get("/", tags=["System"])
def root():
    return {
        "title": "Space Bounty Hunters REST API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "criminals": "/api/criminals/",
            "hunts": "/api/hunts/",
        },
    }


@app.get("/api/health", tags=["System"])
def health_check():
    db_connected = ping_db()
    return {
        "status": "healthy" if db_connected else "degraded",
        "database_connected": db_connected,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
