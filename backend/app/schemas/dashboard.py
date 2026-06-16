from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DailyTrendItem(BaseModel):
    date: str
    value: float

class ApplianceBreakdownItem(BaseModel):
    name: str
    kwh: float
    percentage: float

class GreenScoreData(BaseModel):
    current: float
    trend: str
    change_from_last_week: float

class ImpactData(BaseModel):
    co2_reduced_kg: float
    water_saved_liters: float
    money_saved_usd: float
    trees_equivalent: float

class EnergyData(BaseModel):
    today_kwh: float
    week_total_kwh: float
    month_total_kwh: float
    daily_trend: List[DailyTrendItem]
    by_appliance: List[ApplianceBreakdownItem]

class WaterData(BaseModel):
    today_liters: float
    week_total_liters: float
    daily_trend: List[DailyTrendItem]

class VampireDevice(BaseModel):
    id: str
    name: str
    standby_watts: float
    yearly_cost: float

class VampireData(BaseModel):
    count: int
    devices: List[VampireDevice]

class ChallengeItem(BaseModel):
    id: str
    title: str
    progress: float
    target: float
    unit: str

class ChallengesData(BaseModel):
    count: int
    challenges: List[ChallengeItem]

class PeriodData(BaseModel):
    start: datetime
    end: datetime
    timezone: str

class DashboardSummary(BaseModel):
    green_score: GreenScoreData
    impact: ImpactData
    energy: EnergyData
    water: WaterData
    energy_vampires: VampireData
    active_challenges: ChallengesData
    period: PeriodData
