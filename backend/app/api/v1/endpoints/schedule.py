from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.services.schedule_service import ScheduleService
from app.services.grid_service import GridService
from app.schemas.schedule import ScheduleResponse, GridForecastHour, SchedulePreferencesResponse, SchedulePreferencesBase
from app.models.schedule import ScheduleRecommendation, SchedulePreferences

router = APIRouter()

@router.get("/recommendations", response_model=ScheduleResponse)
async def get_recommendations(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ScheduleService.generate_recommendations(db, current_user.id)

@router.get("/grid-forecast", response_model=List[GridForecastHour])
async def get_grid_forecast():
    return GridService.generate_grid_forecast()

@router.post("/accept/{rec_id}")
async def accept_recommendation(
    rec_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ScheduleRecommendation).where(ScheduleRecommendation.id == rec_id, ScheduleRecommendation.user_id == current_user.id))
    rec = result.scalars().first()
    if not rec: raise HTTPException(404)
    rec.status = "accepted"
    await db.commit()
    return {"status": "accepted"}

@router.post("/dismiss/{rec_id}")
async def dismiss_recommendation(
    rec_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ScheduleRecommendation).where(ScheduleRecommendation.id == rec_id, ScheduleRecommendation.user_id == current_user.id))
    rec = result.scalars().first()
    if not rec: raise HTTPException(404)
    rec.status = "dismissed"
    await db.commit()
    return {"status": "dismissed"}

@router.get("/preferences", response_model=SchedulePreferencesResponse)
async def get_preferences(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ScheduleService.get_or_create_preferences(db, current_user.id)

@router.put("/preferences", response_model=SchedulePreferencesResponse)
async def update_preferences(
    prefs_in: SchedulePreferencesBase,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prefs = await ScheduleService.get_or_create_preferences(db, current_user.id)
    prefs.priority = prefs_in.priority
    prefs.quiet_hours_start = prefs_in.quiet_hours_start
    prefs.quiet_hours_end = prefs_in.quiet_hours_end
    prefs.auto_schedule = prefs_in.auto_schedule
    await db.commit()
    await db.refresh(prefs)
    return prefs
