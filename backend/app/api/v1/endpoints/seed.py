from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.services.seeder_service import SeederService

router = APIRouter()

@router.post("")
async def seed_user_data(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate 30 days of realistic mock IoT data (appliances, energy, water) for the current user.
    """
    await SeederService.seed_data_for_user(db, current_user.id)
    return {"message": "Data successfully seeded!"}
