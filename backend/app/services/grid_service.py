from datetime import datetime, timedelta, timezone
from app.schemas.schedule import GridForecastHour
import random

class GridService:
    @staticmethod
    def generate_grid_forecast(hours: int = 24) -> list[GridForecastHour]:
        """Generates realistic mock grid data starting from the current hour."""
        forecast = []
        now = datetime.now(timezone.utc)
        
        for i in range(hours):
            target_hour = (now + timedelta(hours=i)).hour
            
            # Base logic from Phase 6 spec
            if 0 <= target_hour <= 5:
                demand_level = "low"
                load_pct = random.uniform(30, 40)
                carbon_intensity = 200
                solar_pct = 0
                wind_pct = random.uniform(10, 20)
                tier = "off_peak"
                rate = 0.08
            elif 6 <= target_hour <= 8:
                demand_level = "medium"
                load_pct = random.uniform(50, 65)
                carbon_intensity = 350
                solar_pct = random.uniform(5, 15)
                wind_pct = random.uniform(10, 15)
                tier = "off_peak" if target_hour < 7 else "mid_peak"
                rate = 0.08 if target_hour < 7 else 0.12
            elif 9 <= target_hour <= 11:
                demand_level = "medium"
                load_pct = random.uniform(60, 70)
                carbon_intensity = 380
                solar_pct = random.uniform(25, 40)
                wind_pct = random.uniform(8, 12)
                tier = "mid_peak"
                rate = 0.12
            elif 12 <= target_hour <= 14:
                demand_level = "high"
                load_pct = random.uniform(75, 85)
                carbon_intensity = 420
                solar_pct = random.uniform(45, 55)
                wind_pct = random.uniform(5, 10)
                tier = "mid_peak"
                rate = 0.12
            elif 15 <= target_hour <= 17:
                demand_level = "high"
                load_pct = random.uniform(80, 90)
                carbon_intensity = 450
                solar_pct = random.uniform(20, 35)
                wind_pct = random.uniform(10, 15)
                tier = "mid_peak" if target_hour < 16 else "on_peak"
                rate = 0.12 if target_hour < 16 else 0.22
            elif 18 <= target_hour <= 20:
                demand_level = "peak"
                load_pct = random.uniform(90, 100)
                carbon_intensity = 500
                solar_pct = random.uniform(0, 10)
                wind_pct = random.uniform(15, 20)
                tier = "on_peak"
                rate = 0.22
            else: # 21-23
                demand_level = "medium"
                load_pct = random.uniform(55, 65)
                carbon_intensity = 320
                solar_pct = 0
                wind_pct = random.uniform(15, 25)
                tier = "mid_peak" if target_hour < 23 else "off_peak"
                rate = 0.12 if target_hour < 23 else 0.08
                
            total_renewable = solar_pct + wind_pct
                
            forecast.append(GridForecastHour(
                hour=target_hour,
                demand_level=demand_level,
                load_percentage=round(load_pct, 1),
                carbon_intensity_gco2_kwh=round(carbon_intensity * (1 - (total_renewable / 100)), 1), # Reduce carbon if high renewables
                solar_percentage=round(solar_pct, 1),
                wind_percentage=round(wind_pct, 1),
                total_renewable_percentage=round(total_renewable, 1),
                is_green_peak=total_renewable > 40,
                rate_usd=rate,
                pricing_tier=tier
            ))
            
        return forecast
