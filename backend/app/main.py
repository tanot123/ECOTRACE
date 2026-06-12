from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, users
from app.api.v1.endpoints import dashboard

from app.database import engine, Base
import app.models.user
import app.models.appliance
import app.models.reading

app = FastAPI(
    title="EcoTrace AI API",
    description="Backend API for EcoTrace AI MVP",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
from app.api.v1.endpoints import seed, energy
app.include_router(seed.router, prefix="/api/v1/seed", tags=["seed"])
app.include_router(energy.router, prefix="/api/v1/energy", tags=["energy"])

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health_check():
    return {"status": "healthy"}
