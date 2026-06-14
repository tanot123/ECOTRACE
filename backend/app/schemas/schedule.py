from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class SchedulePreferencesBase(BaseModel):
    priority: str
    quiet_hours_start: int
    quiet_hours_end: int
    auto_schedule: bool

class SchedulePreferencesResponse(SchedulePreferencesBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)

class GridForecastHour(BaseModel):
    hour: int
    demand_level: str
    load_percentage: float
    carbon_intensity_gco2_kwh: float
    solar_percentage: float
    wind_percentage: float
    total_renewable_percentage: float
    is_green_peak: bool
    rate_usd: float
    pricing_tier: str

class ScheduleRecommendationBase(BaseModel):
    appliance_id: UUID
    appliance_name: str
    recommended_start: str
    recommended_end: str
    estimated_cost_usd: float
    carbon_saved_grams: float
    money_saved_usd: float
    renewable_percentage: float
    reasoning: str
    priority_rank: int

class ScheduleRecommendationResponse(ScheduleRecommendationBase):
    id: UUID
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DailySummary(BaseModel):
    total_estimated_cost: float
    total_carbon_saved: float
    best_renewable_window: str
    tip: str

class ScheduleResponse(BaseModel):
    recommendations: List[ScheduleRecommendationResponse]
    daily_summary: DailySummary
    generated_at: datetime
