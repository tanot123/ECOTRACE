from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, extract
from app.models.appliance import Appliance
from app.models.reading import EnergyReading, WaterReading
from app.schemas.dashboard import (
    DashboardSummary, GreenScoreData, ImpactData, EnergyData, WaterData, 
    VampireData, ChallengesData, PeriodData, DailyTrendItem, ApplianceBreakdownItem,
    VampireDevice, ChallengeItem
)

class GreenScoreService:
    @staticmethod
    async def get_dashboard_summary(db: AsyncSession, user_id: str) -> DashboardSummary:
        today = datetime.now(timezone.utc)
        week_ago = today - timedelta(days=7)
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 1. Fetch Appliances
        appliances_res = await db.execute(select(Appliance).where(Appliance.user_id == user_id))
        appliances = appliances_res.scalars().all()
        appliance_ids = [a.id for a in appliances]
        appliance_map = {a.id: a.name for a in appliances}
        
        # 2. Daily Energy Trend (last 7 days)
        # Using a simpler query for SQLite/Postgres compatibility: fetch last 7 days and aggregate in Python
        energy_res = await db.execute(
            select(EnergyReading).where(
                EnergyReading.appliance_id.in_(appliance_ids),
                EnergyReading.recorded_at >= week_ago
            )
        )
        energy_readings = energy_res.scalars().all()
        
        daily_kwh = {}
        appliance_kwh = {a.id: 0.0 for a in appliances}
        today_kwh = 0.0
        week_kwh = 0.0
        
        for r in energy_readings:
            date_str = r.recorded_at.strftime("%Y-%m-%d")
            daily_kwh[date_str] = daily_kwh.get(date_str, 0.0) + r.kwh_consumed
            appliance_kwh[r.appliance_id] += r.kwh_consumed
            week_kwh += r.kwh_consumed
            if r.recorded_at >= today_start:
                today_kwh += r.kwh_consumed
                
        energy_trend = [
            DailyTrendItem(date=(today - timedelta(days=i)).strftime("%Y-%m-%d"), value=round(daily_kwh.get((today - timedelta(days=i)).strftime("%Y-%m-%d"), 0.0), 1))
            for i in range(6, -1, -1)
        ]
        
        by_appliance = []
        if week_kwh > 0:
            for a_id, kwh in appliance_kwh.items():
                if kwh > 0:
                    by_appliance.append(ApplianceBreakdownItem(
                        name=appliance_map[a_id], 
                        kwh=round(kwh, 1), 
                        percentage=round((kwh / week_kwh) * 100, 1)
                    ))
        by_appliance.sort(key=lambda x: x.kwh, reverse=True)
        
        # 3. Water Data
        water_res = await db.execute(select(WaterReading).where(WaterReading.user_id == user_id, WaterReading.recorded_at >= week_ago))
        water_readings = water_res.scalars().all()
        
        daily_water = {}
        today_liters = 0.0
        week_liters = 0.0
        
        for w in water_readings:
            date_str = w.recorded_at.strftime("%Y-%m-%d")
            daily_water[date_str] = daily_water.get(date_str, 0.0) + w.liters
            week_liters += w.liters
            if w.recorded_at >= today_start:
                today_liters += w.liters
                
        water_trend = [
            DailyTrendItem(date=(today - timedelta(days=i)).strftime("%Y-%m-%d"), value=round(daily_water.get((today - timedelta(days=i)).strftime("%Y-%m-%d"), 0.0), 1))
            for i in range(6, -1, -1)
        ]
        
        # 4. Vampires
        vampires = [a for a in appliances if a.is_energy_vampire]
        vampire_devices = []
        for v in vampires:
            vampire_devices.append(VampireDevice(
                name=v.name,
                standby_watts=v.standby_watts,
                yearly_cost=round((v.standby_watts / 1000) * (24 - v.avg_daily_hours) * 365 * 0.12, 2)
            ))
            
        # 5. Green Score Computation (Simple)
        # Base 100, subtract for high usage
        score = 85.0
        if week_kwh > 100: score -= 5
        if week_liters > 2000: score -= 5
        score -= min(15, len(vampires) * 2)
        
        return DashboardSummary(
            green_score=GreenScoreData(
                current=round(score, 1),
                trend="up",
                change_from_last_week=1.2
            ),
            impact=ImpactData(
                co2_reduced_kg=round(week_kwh * 0.417, 1),
                water_saved_liters=round(2500 - week_liters, 1) if week_liters < 2500 else 0,
                money_saved_usd=round(18.50, 2), # Static for now
                trees_equivalent=round((week_kwh * 0.417) / 21.77, 2)
            ),
            energy=EnergyData(
                today_kwh=round(today_kwh, 1),
                week_total_kwh=round(week_kwh, 1),
                month_total_kwh=round(week_kwh * 4, 1),
                daily_trend=energy_trend,
                by_appliance=by_appliance[:5]
            ),
            water=WaterData(
                today_liters=round(today_liters, 1),
                week_total_liters=round(week_liters, 1),
                daily_trend=water_trend
            ),
            energy_vampires=VampireData(
                count=len(vampire_devices),
                devices=vampire_devices[:3]
            ),
            active_challenges=ChallengesData(
                count=3,
                challenges=[
                    ChallengeItem(id="c1", title="Turn off AC for 2 hours", progress=1.5, target=2.0, unit="hrs"),
                    ChallengeItem(id="c2", title="Keep showers under 5 min", progress=3.0, target=7.0, unit="days"),
                    ChallengeItem(id="c3", title="Unplug Vampire Devices", progress=1.0, target=3.0, unit="devices"),
                ]
            ),
            period=PeriodData(
                start=week_ago,
                end=today,
                timezone="UTC"
            )
        )
