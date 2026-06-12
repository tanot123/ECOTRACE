from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ApplianceBase(BaseModel):
    name: str
    category: str
    icon: Optional[str] = None
    active_watts: float
    standby_watts: float = 0.0
    avg_daily_hours: float = 1.0
    is_active: bool = True

class ApplianceCreate(ApplianceBase):
    pass

class ApplianceResponse(ApplianceBase):
    id: UUID
    user_id: UUID
    is_energy_vampire: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EnergyReadingResponse(BaseModel):
    id: UUID
    appliance_id: UUID
    kwh_consumed: float
    is_standby: bool
    cost_estimate: float
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WaterReadingResponse(BaseModel):
    id: UUID
    user_id: UUID
    liters: float
    source: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VampireSuggestion(BaseModel):
    appliance_id: UUID
    appliance_name: str
    category: str
    standby_watts: float
    standby_hours_per_day: float
    daily_vampire_kwh: float
    yearly_vampire_cost: float
    suggestion: str
    is_resolved: bool = False

class RealtimeEnergyReading(BaseModel):
    appliance_name: str
    watts: float
    status: str

class RealtimeEnergyResponse(BaseModel):
    timestamp: datetime
    total_watts_now: float
    total_kwh_today: float
    active_appliances: int
    readings: List[RealtimeEnergyReading]
