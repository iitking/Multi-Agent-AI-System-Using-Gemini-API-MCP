import logging
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import settings
from backend.database.session import init_db
from backend.database.init_db import seed_data
from backend.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("enterprise-multi-agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Enterprise Multi-Agent System backend...")
    await init_db()
    try:
        await seed_data()
    except Exception as e:
        logger.warning(f"Database seed note: {e}")
    logger.info("System ready. Gemini API + LangGraph + MCP initialized.")
    yield
    logger.info("Shutting down backend services.")


app = FastAPI(
    title="Enterprise Multi-Agent AI System",
    description="Operations and Intelligence Platform powered by Google Gemini API, LangGraph, and Model Context Protocol (MCP).",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


@app.get("/")
async def root():
    """Root entrypoint with service metadata and links."""
    return {
        "service": "Enterprise Multi-Agent AI System",
        "status": "online",
        "dashboard_ui": "http://localhost:3000",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "create_run": "POST /api/v1/runs",
            "list_runs": "GET /api/v1/runs",
            "mcp_tools": "GET /api/v1/tools",
            "metrics": "GET /api/v1/metrics",
            "audit_trail": "GET /api/v1/audit"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Enterprise Multi-Agent System",
        "gemini_model": settings.GEMINI_MODEL,
        "environment": settings.ENVIRONMENT,
        "n8n_enabled": settings.N8N_ENABLED,
        "mcp_servers": ["Data_MCP_Server", "Research_MCP_Server", "Document_MCP_Server", "Automation_MCP_Server"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
