from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.endpoints import dashboard, auth, users

from app.database import engine, Base
import app.models.user
import app.models.appliance
import app.models.reading
import app.models.scan
import app.models.schedule
import app.models.challenge

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="EcoTrace AI API",
    description="Backend API for EcoTrace AI MVP",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
from app.api.v1.endpoints import seed, energy, scan, schedule, challenges
app.include_router(seed.router, prefix="/api/v1/seed", tags=["seed"])
app.include_router(energy.router, prefix="/api/v1/energy", tags=["energy"])
app.include_router(scan.router, prefix="/api/v1/scan", tags=["scan"])
app.include_router(schedule.router, prefix="/api/v1/schedule", tags=["schedule"])
app.include_router(challenges.router, prefix="/api/v1/challenges", tags=["challenges"])

@app.get("/api/v1/health", tags=["health"])
async def api_health_check():
    return {"status": "healthy"}
