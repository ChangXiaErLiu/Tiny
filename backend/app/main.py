"""FastAPI application entry point for declarative skill framework."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from .api.v1 import chat, skill, health, trace
from .core.skill.registry import SkillRegistry
from .config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def get_skills_base_path() -> str:
    """Get the base path for skills directory."""
    base_path = os.path.join(os.path.dirname(__file__), "skills")
    return base_path


def register_skills_from_filesystem(registry: SkillRegistry):
    """Load and register all declarative skills from filesystem."""
    skills_base_path = get_skills_base_path()
    logger.info(f"Loading skills from: {skills_base_path}")

    registry.initialize(skills_base_path)

    manifests = registry.list_all()
    logger.info(f"Registered {len(manifests)} declarative skills:")

    for manifest in manifests:
        logger.info(f"  - {manifest.name} v{manifest.version}: {manifest.description[:50]}...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Agent Skill Framework (Declarative)...")

    registry = SkillRegistry()
    register_skills_from_filesystem(registry)

    logger.info("Application startup complete")

    yield

    logger.info("Shutting down Agent Skill Framework...")


app = FastAPI(
    title="Agent Skill Framework (Declarative)",
    description="A declarative skill development framework where skills are defined by SKILL.md, script.py, and reference files",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["chat"]
)

app.include_router(
    skill.router,
    prefix="/api/v1/skills",
    tags=["skills"]
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"]
)

app.include_router(
    trace.router,
    prefix="/api/v1",
    tags=["trace"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    registry = SkillRegistry()
    skills = registry.list_all()

    return {
        "name": "Agent Skill Framework (Declarative)",
        "version": "2.0.0",
        "description": "Skills are defined by SKILL.md + script.py + references",
        "docs": "/docs",
        "health": "/api/v1/health",
        "registered_skills": [
            {
                "name": m.name,
                "version": m.version,
                "description": m.description
            }
            for m in skills
        ]
    }
