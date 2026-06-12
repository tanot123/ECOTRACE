import random
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.appliance import Appliance
from app.models.reading import EnergyReading, WaterReading
from uuid import UUID

DEFAULT_APPLIANCES = [
    {"name": "Refrigerator", "category": "kitchen", "active_watts": 150, "standby_watts": 2, "avg_daily_hours": 24},
    {"name": "Washing Machine", "category": "laundry", "active_watts": 500, "standby_watts": 5, "avg_daily_hours": 1},
    {"name": "Clothes Dryer", "category": "laundry", "active_watts": 3000, "standby_watts": 3, "avg_daily_hours": 0.5},
    {"name": "Dishwasher", "category": "kitchen", "active_watts": 1800, "standby_watts": 4, "avg_daily_hours": 1},
    {"name": "Television (55\")", "category": "entertainment", "active_watts": 100, "standby_watts": 12, "avg_daily_hours": 5},
    {"name": "Gaming Console", "category": "entertainment", "active_watts": 200, "standby_watts": 15, "avg_daily_hours": 2},
    {"name": "Desktop Computer", "category": "office", "active_watts": 300, "standby_watts": 8, "avg_daily_hours": 6},
    {"name": "Microwave", "category": "kitchen", "active_watts": 1200, "standby_watts": 3, "avg_daily_hours": 0.25},
    {"name": "Air Conditioner", "category": "hvac", "active_watts": 3500, "standby_watts": 0, "avg_daily_hours": 8},
    {"name": "Water Heater", "category": "utility", "active_watts": 4500, "standby_watts": 0, "avg_daily_hours": 3},
    {"name": "Smart Speaker", "category": "entertainment", "active_watts": 6, "standby_watts": 4, "avg_daily_hours": 24},
    {"name": "Cable/Satellite Box", "category": "entertainment", "active_watts": 35, "standby_watts": 26, "avg_daily_hours": 6},
]

class SeederService:
    @staticmethod
    async def seed_data_for_user(db: AsyncSession, user_id: UUID, days: int = 30) -> None:
        """Seed default appliances and realistic time-series data for a user."""
        # 1. Check if user already has data. If so, wipe it to be idempotent.
        await db.execute(delete(Appliance).where(Appliance.user_id == user_id))
        await db.execute(delete(WaterReading).where(WaterReading.user_id == user_id))
        await db.commit()

        # 2. Insert Appliances
        appliances = []
        for app_data in DEFAULT_APPLIANCES:
            appliance = Appliance(
                user_id=user_id,
                name=app_data["name"],
                category=app_data["category"],
                active_watts=app_data["active_watts"],
                standby_watts=app_data["standby_watts"],
                avg_daily_hours=app_data["avg_daily_hours"],
                is_energy_vampire=(app_data["standby_watts"] > 5)
            )
            db.add(appliance)
            appliances.append(appliance)
        
        await db.commit()
        for a in appliances: await db.refresh(a)

        # 3. Generate Energy Readings (15 min intervals)
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        rate_per_kwh = 0.12
        energy_readings_to_insert = []
        water_readings_to_insert = []

        time_multipliers = {
            (0, 5): 0.3,
            (6, 8): 0.7,
            (9, 11): 0.5,
            (12, 13): 0.6,
            (14, 16): 0.5,
            (17, 19): 0.9,
            (20, 22): 0.8,
            (23, 23): 0.4
        }

        def get_multiplier(hour: int, is_weekend: bool) -> float:
            base_mult = 1.0
            for (start_h, end_h), mult in time_multipliers.items():
                if start_h <= hour <= end_h:
                    base_mult = mult
                    break
            
            if is_weekend:
                # Shift pattern
                if 8 <= hour <= 11: base_mult *= 1.4 # Later morning activity
                if 14 <= hour <= 22: base_mult *= 1.2 # More entertainment
                
            return base_mult

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            is_weekend = current_date.weekday() >= 5
            
            # Water per day
            # Shower
            water_readings_to_insert.append(WaterReading(user_id=user_id, liters=65.0 * random.uniform(0.8, 1.2), source="shower", recorded_at=current_date.replace(hour=7)))
            water_readings_to_insert.append(WaterReading(user_id=user_id, liters=65.0 * random.uniform(0.8, 1.2), source="shower", recorded_at=current_date.replace(hour=21)))
            # Toilet
            water_readings_to_insert.append(WaterReading(user_id=user_id, liters=48.0 * random.uniform(0.9, 1.1), source="toilet", recorded_at=current_date.replace(hour=12)))
            # Faucet
            water_readings_to_insert.append(WaterReading(user_id=user_id, liters=45.0 * random.uniform(0.8, 1.2), source="faucet", recorded_at=current_date.replace(hour=18)))
            
            if not is_weekend and day_offset % 3 == 0:
                water_readings_to_insert.append(WaterReading(user_id=user_id, liters=50.0, source="washing_machine", recorded_at=current_date.replace(hour=19)))
            
            if random.random() > 0.3:
                water_readings_to_insert.append(WaterReading(user_id=user_id, liters=22.0, source="dishwasher", recorded_at=current_date.replace(hour=20)))

            # Energy per 15 mins
            for hour in range(24):
                multiplier = get_multiplier(hour, is_weekend)
                for minute in (0, 15, 30, 45):
                    recorded_time = current_date.replace(hour=hour, minute=minute)
                    
                    for app in appliances:
                        # Probability of being active based on avg_daily_hours and multiplier
                        prob_active = (app.avg_daily_hours / 24.0) * multiplier
                        if app.name == "Refrigerator": prob_active = 1.0
                        
                        is_active = random.random() < prob_active
                        
                        if is_active:
                            kwh = (app.active_watts / 1000.0) * 0.25 * random.uniform(0.85, 1.15)
                            is_standby = False
                        else:
                            kwh = (app.standby_watts / 1000.0) * 0.25 * random.uniform(0.9, 1.1)
                            is_standby = True
                            
                        energy_readings_to_insert.append(
                            EnergyReading(
                                appliance_id=app.id,
                                kwh_consumed=kwh,
                                is_standby=is_standby,
                                cost_estimate=kwh * rate_per_kwh,
                                recorded_at=recorded_time
                            )
                        )
            
            # Batch insert to avoid huge memory spike
            db.add_all(water_readings_to_insert)
            db.add_all(energy_readings_to_insert)
            await db.commit()
            water_readings_to_insert.clear()
            energy_readings_to_insert.clear()
