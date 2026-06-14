from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ChallengeBase(BaseModel):
    title: str
    description: str
    short_description: str
    category: str
    difficulty: str
    metric_type: str
    target_value: float
    target_unit: str
    comparison: str
    duration_days: int
    points: int
    icon: str

class ChallengeResponse(ChallengeBase):
    id: UUID
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserChallengeResponse(BaseModel):
    id: UUID
    user_id: UUID
    challenge_id: UUID
    current_progress: float
    target_value: float
    status: str
    points_earned: int
    started_at: datetime
    expires_at: datetime
    completed_at: Optional[datetime] = None
    challenge: Optional[ChallengeResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class ChallengeStats(BaseModel):
    total_points: int
    current_level_title: str
    current_level_num: int
    points_to_next_level: int
    challenges_completed: int
    active_challenges_count: int
