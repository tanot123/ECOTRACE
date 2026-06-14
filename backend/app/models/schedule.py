from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base

class SchedulePreferences(Base):
    __tablename__ = "schedule_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    priority = Column(String, default="balanced") # save_money, reduce_carbon, balanced
    quiet_hours_start = Column(Integer, default=22) # 0-23
    quiet_hours_end = Column(Integer, default=7) # 0-23
    auto_schedule = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ScheduleRecommendation(Base):
    __tablename__ = "schedule_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    appliance_id = Column(UUID(as_uuid=True), ForeignKey("appliances.id", ondelete="CASCADE"), nullable=False)
    appliance_name = Column(String, nullable=False)
    recommended_start = Column(String, nullable=False) # HH:MM
    recommended_end = Column(String, nullable=False) # HH:MM
    estimated_cost_usd = Column(Float, nullable=False)
    carbon_saved_grams = Column(Float, nullable=False)
    money_saved_usd = Column(Float, nullable=False)
    renewable_percentage = Column(Float, nullable=False)
    reasoning = Column(String, nullable=False)
    priority_rank = Column(Integer, nullable=False)
    status = Column(String, default="pending") # pending, accepted, dismissed, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
