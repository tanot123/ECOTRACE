from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_user
from app.services.challenge_service import ChallengeService
from app.schemas.challenge import ChallengeResponse, UserChallengeResponse, ChallengeStats

router = APIRouter()

@router.post("/seed")
async def seed_challenges(db: AsyncSession = Depends(get_db)):
    await ChallengeService.seed_challenges(db)
    return {"status": "seeded"}

@router.get("/stats", response_model=ChallengeStats)
async def get_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChallengeService.get_stats(db, current_user.id)

@router.get("/available", response_model=List[ChallengeResponse])
async def get_available(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChallengeService.get_available(db, current_user.id)

@router.get("/active", response_model=List[UserChallengeResponse])
async def get_active(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChallengeService.get_active(db, current_user.id)

@router.get("/completed", response_model=List[UserChallengeResponse])
async def get_completed(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChallengeService.get_completed(db, current_user.id)

@router.post("/{challenge_id}/start", response_model=UserChallengeResponse)
async def start_challenge(
    challenge_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await ChallengeService.start_challenge(db, current_user.id, challenge_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_challenge_id}/evaluate", response_model=UserChallengeResponse)
async def evaluate_challenge(
    user_challenge_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChallengeService.evaluate_progress(db, current_user.id, user_challenge_id)

@router.post("/{user_challenge_id}/abandon")
async def abandon_challenge(
    user_challenge_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await ChallengeService.abandon_challenge(db, current_user.id, user_challenge_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
