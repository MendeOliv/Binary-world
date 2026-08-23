from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Import routers
from app.routers.projects import router as projects_router
from app.routers.decisions import project_decisions_router, decisions_router
from app.routers.requirements import router as requirements_router
from app.routers.tasks import project_tasks_router, tasks_router
from app.routers.memory import router as memory_router
from app.routers.chat import router as chat_router
from app.routers.logs import router as logs_router
from app.routers.conflicts import router as conflicts_router

app = FastAPI(
    title="Hermes Backend Orchestrator",
    description=(
        "The continuity & memory orchestrator for Código Binário. "
        "Implements the repository-first principle: every request queries the database "
        "before calling any AI model."
    ),
    version="1.0.0"
)

# Configure CORS origins
if settings.ALLOWED_ORIGINS == "*":
    allowed_origins_list = ["*"]
else:
    allowed_origins_list = [
        origin.strip()
        for origin in settings.ALLOWED_ORIGINS.split(",")
        if origin.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials="*" not in allowed_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck endpoint (no API key authentication required)
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "provider": settings.PRIMARY_PROVIDER,
        "database_configured": settings.SUPABASE_URL != "https://placeholder-project.supabase.co"
    }

# Register all API Routers
app.include_router(projects_router)
app.include_router(project_decisions_router)
app.include_router(decisions_router)
app.include_router(requirements_router)
app.include_router(project_tasks_router)
app.include_router(tasks_router)
app.include_router(memory_router)
app.include_router(chat_router)
app.include_router(logs_router)
app.include_router(conflicts_router)
