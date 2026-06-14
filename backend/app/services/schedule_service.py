import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.appliance import Appliance
from app.models.schedule import SchedulePreferences, ScheduleRecommendation
from app.schemas.schedule import ScheduleResponse
from app.services.grid_service import GridService
from app.config import settings
import google.generativeai as genai
from uuid import UUID

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

class ScheduleService:
    @staticmethod
    async def get_or_create_preferences(db: AsyncSession, user_id: UUID) -> SchedulePreferences:
        result = await db.execute(select(SchedulePreferences).where(SchedulePreferences.user_id == user_id))
        prefs = result.scalars().first()
        if not prefs:
            prefs = SchedulePreferences(user_id=user_id)
            db.add(prefs)
            await db.commit()
            await db.refresh(prefs)
        return prefs

    @staticmethod
    async def generate_recommendations(db: AsyncSession, user_id: UUID) -> ScheduleResponse:
        # Check cache (6 hours)
        six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)
        existing_result = await db.execute(
            select(ScheduleRecommendation)
            .where(ScheduleRecommendation.user_id == user_id)
            .where(ScheduleRecommendation.created_at >= six_hours_ago)
        )
        existing = existing_result.scalars().all()
        
        # We need a summary if we return cached, but let's assume we regenerate if we don't have enough data
        if not existing:
            await db.execute(delete(ScheduleRecommendation).where(ScheduleRecommendation.user_id == user_id))
            await db.commit()

            # Fetch heavy appliances
            app_result = await db.execute(
                select(Appliance)
                .where(Appliance.user_id == user_id, Appliance.active_watts > 500)
            )
            appliances = app_result.scalars().all()

            if not appliances:
                # Return empty
                return {
                    "recommendations": [],
                    "daily_summary": {
                        "total_estimated_cost": 0,
                        "total_carbon_saved": 0,
                        "best_renewable_window": "N/A",
                        "tip": "Add a high-wattage appliance (like a Washing Machine) to get AI scheduling."
                    },
                    "generated_at": datetime.now(timezone.utc)
                }

            prefs = await ScheduleService.get_or_create_preferences(db, user_id)
            grid_forecast = GridService.generate_grid_forecast()

            # Assemble context
            context = {
                "appliances": [{"name": a.name, "watts": a.active_watts, "duration_minutes": int(a.avg_daily_hours * 60)} for a in appliances],
                "grid_forecast": [f.model_dump() for f in grid_forecast],
                "user_preferences": {
                    "priority": prefs.priority,
                    "quiet_hours": {"start": prefs.quiet_hours_start, "end": prefs.quiet_hours_end}
                },
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "day_of_week": datetime.now(timezone.utc).strftime("%A")
            }

            prompt = f"""
            You are an expert energy optimization advisor for smart homes.
            Given the following household data, recommend the best time slots to run each appliance over the next 24 hours.

            CONTEXT:
            {json.dumps(context, indent=2)}

            OPTIMIZATION GOALS (priority: {prefs.priority}):
            - save_money: Minimize electricity cost by scheduling during off-peak rates.
            - reduce_carbon: Minimize carbon footprint by scheduling during high renewable energy periods.
            - balanced: Optimize for both cost savings and carbon reduction.

            CONSTRAINTS:
            - Noisy appliances must NOT be scheduled during quiet hours ({prefs.quiet_hours_start}:00 - {prefs.quiet_hours_end}:00).
            - Do not schedule multiple high-wattage appliances (>1500W) in the same time slot.
            - Each appliance should be scheduled exactly once.

            Respond ONLY with valid JSON in this exact format, with no markdown code blocks wrapping it:
            {{
              "recommendations": [
                {{
                  "appliance_name": "appliance name",
                  "recommended_start": "HH:MM",
                  "recommended_end": "HH:MM",
                  "estimated_cost": 0.50,
                  "carbon_saved_vs_peak": 120,
                  "money_saved_vs_peak": 0.20,
                  "renewable_percentage": 45.5,
                  "reasoning": "Reason here",
                  "priority_rank": 1
                }}
              ],
              "daily_summary": {{
                "total_estimated_cost": 1.20,
                "total_carbon_saved": 400.0,
                "best_renewable_window": "10:00 - 14:00",
                "tip": "Run appliances at noon to maximize solar."
              }}
            }}
            """

            response = await model.generate_content_async(prompt)
            
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            parsed = json.loads(text.strip())

            # Map generated names back to appliance IDs
            recs_to_save = []
            for rec in parsed.get("recommendations", []):
                app_obj = next((a for a in appliances if a.name == rec["appliance_name"]), None)
                if app_obj:
                    r = ScheduleRecommendation(
                        user_id=user_id,
                        appliance_id=app_obj.id,
                        appliance_name=app_obj.name,
                        recommended_start=rec["recommended_start"],
                        recommended_end=rec["recommended_end"],
                        estimated_cost_usd=rec["estimated_cost"],
                        carbon_saved_grams=rec["carbon_saved_vs_peak"],
                        money_saved_usd=rec["money_saved_vs_peak"],
                        renewable_percentage=rec["renewable_percentage"],
                        reasoning=rec["reasoning"],
                        priority_rank=rec["priority_rank"],
                        status="pending"
                    )
                    db.add(r)
                    recs_to_save.append(r)
            
            await db.commit()
            for r in recs_to_save: await db.refresh(r)
            existing = recs_to_save
            summary = parsed.get("daily_summary")
        else:
            # We don't cache the daily_summary currently in DB so we'll mock it if cached
            summary = {
                "total_estimated_cost": sum(e.estimated_cost_usd for e in existing),
                "total_carbon_saved": sum(e.carbon_saved_grams for e in existing),
                "best_renewable_window": "Calculated previously",
                "tip": "Follow your generated schedule to save energy."
            }

        return {
            "recommendations": existing,
            "daily_summary": summary,
            "generated_at": datetime.now(timezone.utc)
        }
