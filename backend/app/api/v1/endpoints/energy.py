from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime
import random
from app.database import get_db
from app.dependencies import get_current_user
from app.models.appliance import Appliance
from app.schemas.energy import ApplianceResponse, ApplianceCreate, VampireSuggestion, RealtimeEnergyResponse, RealtimeEnergyReading

router = APIRouter()

@router.get("/appliances", response_model=List[ApplianceResponse])
async def get_appliances(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Appliance).where(Appliance.user_id == current_user.id))
    return result.scalars().all()

@router.post("/appliances", response_model=ApplianceResponse)
async def add_appliance(
    appliance_in: ApplianceCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    appliance = Appliance(
        **appliance_in.model_dump(),
        user_id=current_user.id,
        is_energy_vampire=(appliance_in.standby_watts > 5)
    )
    db.add(appliance)
    await db.commit()
    await db.refresh(appliance)
    return appliance

@router.get("/realtime", response_model=RealtimeEnergyResponse)
async def get_realtime_energy(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # This is a simulated real-time response endpoint.
    result = await db.execute(select(Appliance).where(Appliance.user_id == current_user.id))
    appliances = result.scalars().all()
    
    readings = []
    total_watts = 0.0
    active_count = 0
    
    for app in appliances:
        # 30% chance to be active for the simulation
        is_active = random.random() < 0.3
        if app.name == "Refrigerator": is_active = True
        
        watts = app.active_watts if is_active else app.standby_watts
        total_watts += watts
        if is_active: active_count += 1
        
        readings.append(
            RealtimeEnergyReading(
                appliance_name=app.name,
                watts=watts,
                status="active" if is_active else "standby"
            )
        )
        
    return RealtimeEnergyResponse(
        timestamp=datetime.utcnow(),
        total_watts_now=total_watts,
        total_kwh_today=random.uniform(5.0, 15.0), # mock total for now until we aggregate
        active_appliances=active_count,
        readings=readings
    )

@router.get("/vampires", response_model=List[VampireSuggestion])
async def get_vampires(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Appliance).where(
            Appliance.user_id == current_user.id, 
            Appliance.is_energy_vampire == True,
            Appliance.is_active == True
        )
    )
    vampires = result.scalars().all()
    
    suggestions = []
    for v in vampires:
        hours = 24 - v.avg_daily_hours
        kwh = (v.standby_watts / 1000) * hours
        yearly_cost = kwh * 365 * 0.12
        
        # Simple suggestion template
        sugg = "Connect to a smart power strip."
        if v.category == "entertainment": sugg = "Use a smart power strip that cuts power when the main device is off."
        if v.category == "office": sugg = "Enable sleep mode after 10 minutes, or use a master switch."
        
        suggestions.append(
            VampireSuggestion(
                appliance_id=v.id,
                appliance_name=v.name,
                category=v.category,
                standby_watts=v.standby_watts,
                standby_hours_per_day=hours,
                daily_vampire_kwh=round(kwh, 3),
                yearly_vampire_cost=round(yearly_cost, 2),
                suggestion=sugg,
                is_resolved=False
            )
        )
    return suggestions

@router.post("/appliances/{appliance_id}/resolve")
async def resolve_vampire(
    appliance_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from uuid import UUID
    result = await db.execute(select(Appliance).where(Appliance.id == UUID(appliance_id), Appliance.user_id == current_user.id))
    appliance = result.scalars().first()
    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")
        
    appliance.is_active = False
    appliance.updated_at = datetime.utcnow()
    await db.commit()
    return {"status": "resolved"}
