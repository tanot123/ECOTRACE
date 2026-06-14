from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.challenge import Challenge, UserChallenge
from app.models.scan import ScanResult
from app.models.appliance import Appliance
from app.models.schedule import ScheduleRecommendation
from uuid import UUID

LEVELS = [
    (0, "Seedling 🌱"),
    (100, "Sprout 🌿"),
    (300, "Sapling 🌳"),
    (600, "Tree 🌲"),
    (1000, "Forest 🏔️"),
    (1500, "Ecosystem 🌍"),
    (2500, "Guardian 🛡️"),
    (4000, "Champion 🏆"),
    (6000, "Legend ⭐"),
    (10000, "Planet Saver 🌟")
]

DEFAULT_CHALLENGES = [
    {
        "title": "Scan Master", "description": "Scan 5 items for recycling.", "short_description": "Scan 5 items",
        "category": "waste", "difficulty": "easy", "metric_type": "scans_count", "target_value": 5, "target_unit": "scans",
        "comparison": "greater_than", "duration_days": 7, "points": 50, "icon": "📸"
    },
    {
        "title": "Vampire Slayer", "description": "Resolve 3 energy vampires.", "short_description": "Resolve 3 vampires",
        "category": "energy", "difficulty": "medium", "metric_type": "vampire_resolved", "target_value": 3, "target_unit": "appliances",
        "comparison": "greater_than", "duration_days": 7, "points": 75, "icon": "🧛"
    },
    {
        "title": "Peak Dodger", "description": "Accept 3 AI schedule recommendations.", "short_description": "Accept 3 schedules",
        "category": "energy", "difficulty": "medium", "metric_type": "schedule_accepted", "target_value": 3, "target_unit": "recommendations",
        "comparison": "greater_than", "duration_days": 7, "points": 100, "icon": "⏰"
    },
    {
        "title": "Recycling Pro", "description": "Scan 15 items for recycling.", "short_description": "Scan 15 items",
        "category": "waste", "difficulty": "hard", "metric_type": "scans_count", "target_value": 15, "target_unit": "scans",
        "comparison": "greater_than", "duration_days": 14, "points": 150, "icon": "♻️"
    }
]

class ChallengeService:
    @staticmethod
    async def seed_challenges(db: AsyncSession):
        result = await db.execute(select(Challenge))
        existing = result.scalars().all()
        if not existing:
            for c in DEFAULT_CHALLENGES:
                db.add(Challenge(**c))
            await db.commit()

    @staticmethod
    def get_level_info(points: int):
        current_title = LEVELS[0][1]
        current_num = 1
        next_threshold = LEVELS[1][0]
        
        for i, (threshold, title) in enumerate(LEVELS):
            if points >= threshold:
                current_title = title
                current_num = i + 1
                if i + 1 < len(LEVELS):
                    next_threshold = LEVELS[i+1][0]
                else:
                    next_threshold = threshold # Max level
            else:
                break
                
        pts_to_next = next_threshold - points if next_threshold > points else 0
        return current_title, current_num, pts_to_next

    @staticmethod
    async def get_stats(db: AsyncSession, user_id: UUID):
        result = await db.execute(
            select(func.sum(UserChallenge.points_earned))
            .where(UserChallenge.user_id == user_id, UserChallenge.status == "completed")
        )
        points = result.scalar() or 0
        
        completed_res = await db.execute(
            select(func.count(UserChallenge.id))
            .where(UserChallenge.user_id == user_id, UserChallenge.status == "completed")
        )
        completed_count = completed_res.scalar() or 0
        
        active_res = await db.execute(
            select(func.count(UserChallenge.id))
            .where(UserChallenge.user_id == user_id, UserChallenge.status == "active")
        )
        active_count = active_res.scalar() or 0

        title, num, pts_next = ChallengeService.get_level_info(points)

        return {
            "total_points": points,
            "current_level_title": title,
            "current_level_num": num,
            "points_to_next_level": pts_next,
            "challenges_completed": completed_count,
            "active_challenges_count": active_count
        }

    @staticmethod
    async def get_available(db: AsyncSession, user_id: UUID):
        # Return challenges not currently active
        subq = select(UserChallenge.challenge_id).where(UserChallenge.user_id == user_id, UserChallenge.status == "active")
        result = await db.execute(select(Challenge).where(Challenge.id.not_in(subq)))
        return result.scalars().all()

    @staticmethod
    async def get_active(db: AsyncSession, user_id: UUID):
        # Auto-expire if passed expires_at
        now = datetime.now(timezone.utc)
        result = await db.execute(select(UserChallenge).where(UserChallenge.user_id == user_id, UserChallenge.status == "active"))
        active = result.scalars().all()
        
        for uc in active:
            if uc.expires_at < now:
                uc.status = "expired"
                db.add(uc)
        await db.commit()

        # Re-fetch after expiration
        result = await db.execute(select(UserChallenge).where(UserChallenge.user_id == user_id, UserChallenge.status == "active"))
        active_challenges = result.scalars().all()
        
        # Hydrate with Challenge template
        for uc in active_challenges:
            c_res = await db.execute(select(Challenge).where(Challenge.id == uc.challenge_id))
            uc.challenge = c_res.scalars().first()
            
        return active_challenges

    @staticmethod
    async def get_completed(db: AsyncSession, user_id: UUID):
        result = await db.execute(select(UserChallenge).where(UserChallenge.user_id == user_id, UserChallenge.status == "completed"))
        completed = result.scalars().all()
        for uc in completed:
            c_res = await db.execute(select(Challenge).where(Challenge.id == uc.challenge_id))
            uc.challenge = c_res.scalars().first()
        return completed

    @staticmethod
    async def start_challenge(db: AsyncSession, user_id: UUID, challenge_id: UUID):
        # Check max 3
        result = await db.execute(select(func.count(UserChallenge.id)).where(UserChallenge.user_id == user_id, UserChallenge.status == "active"))
        if result.scalar() >= 3:
            raise Exception("Maximum 3 active challenges allowed.")
            
        # Check if already active
        existing = await db.execute(select(UserChallenge).where(UserChallenge.user_id == user_id, UserChallenge.challenge_id == challenge_id, UserChallenge.status == "active"))
        if existing.scalars().first():
            raise Exception("You already have this challenge active.")
            
        c_res = await db.execute(select(Challenge).where(Challenge.id == challenge_id))
        challenge = c_res.scalars().first()
        if not challenge: raise Exception("Challenge not found.")

        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=challenge.duration_days)

        uc = UserChallenge(
            user_id=user_id,
            challenge_id=challenge_id,
            target_value=challenge.target_value,
            expires_at=expires
        )
        db.add(uc)
        await db.commit()
        await db.refresh(uc)
        return uc

    @staticmethod
    async def abandon_challenge(db: AsyncSession, user_id: UUID, user_challenge_id: UUID):
        result = await db.execute(select(UserChallenge).where(UserChallenge.id == user_challenge_id, UserChallenge.user_id == user_id))
        uc = result.scalars().first()
        if not uc or uc.status != "active": raise Exception("Challenge not active or not found.")
        
        uc.status = "failed"
        await db.commit()
        return {"status": "abandoned"}

    @staticmethod
    async def evaluate_progress(db: AsyncSession, user_id: UUID, user_challenge_id: UUID):
        result = await db.execute(select(UserChallenge).where(UserChallenge.id == user_challenge_id, UserChallenge.user_id == user_id))
        uc = result.scalars().first()
        if not uc or uc.status != "active": return uc

        c_res = await db.execute(select(Challenge).where(Challenge.id == uc.challenge_id))
        challenge = c_res.scalars().first()

        now = datetime.now(timezone.utc)
        if uc.expires_at < now:
            uc.status = "expired"
            await db.commit()
            return uc

        # Evaluate based on metric type
        if challenge.metric_type == "scans_count":
            res = await db.execute(select(func.count(ScanResult.id)).where(ScanResult.user_id == user_id, ScanResult.created_at >= uc.started_at))
            uc.current_progress = res.scalar() or 0
        elif challenge.metric_type == "vampire_resolved":
            res = await db.execute(select(func.count(Appliance.id)).where(Appliance.user_id == user_id, Appliance.is_energy_vampire == True, Appliance.is_active == False, Appliance.updated_at >= uc.started_at))
            uc.current_progress = res.scalar() or 0
        elif challenge.metric_type == "schedule_accepted":
            res = await db.execute(select(func.count(ScheduleRecommendation.id)).where(ScheduleRecommendation.user_id == user_id, ScheduleRecommendation.status == "accepted", ScheduleRecommendation.created_at >= uc.started_at))
            uc.current_progress = res.scalar() or 0

        # Check if met target
        if challenge.comparison == "greater_than" and uc.current_progress >= uc.target_value:
            uc.status = "completed"
            uc.points_earned = challenge.points
            uc.completed_at = now
        elif challenge.comparison == "less_than" and uc.current_progress <= uc.target_value:
             # Less than logic is trickier without a continuous monitor. For MVP we skip less_than.
             pass

        await db.commit()
        await db.refresh(uc)
        uc.challenge = challenge
        return uc
