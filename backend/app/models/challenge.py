from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    short_description = Column(String, nullable=False)
    category = Column(String, nullable=False) # energy, water, waste, lifestyle
    difficulty = Column(String, nullable=False) # easy, medium, hard
    metric_type = Column(String, nullable=False) # scans_count, vampire_resolved, schedule_accepted, energy_under_limit
    target_value = Column(Float, nullable=False)
    target_unit = Column(String, nullable=False)
    comparison = Column(String, default="greater_than") # less_than, greater_than
    duration_days = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    icon = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserChallenge(Base):
    __tablename__ = "user_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    current_progress = Column(Float, default=0.0)
    target_value = Column(Float, nullable=False)
    status = Column(String, default="active") # active, completed, failed, expired
    points_earned = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
