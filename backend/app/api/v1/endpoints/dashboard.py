from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.dashboard import DashboardSummary
from app.services.green_score_service import GreenScoreService
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the full dashboard summary data.
    Pulls real aggregated time-series data from PostgreSQL database.
    """
    return await GreenScoreService.get_dashboard_summary(db, str(current_user.id))
