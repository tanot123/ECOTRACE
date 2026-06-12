from sqlalchemy import Column, Float, Boolean, DateTime, ForeignKey, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    appliance_id = Column(UUID(as_uuid=True), ForeignKey("appliances.id", ondelete="CASCADE"), nullable=False)
    kwh_consumed = Column(Float, nullable=False)
    is_standby = Column(Boolean, nullable=False, default=False)
    cost_estimate = Column(Float, nullable=False, default=0.0)
    recorded_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index('ix_energy_readings_appliance_recorded', 'appliance_id', 'recorded_at'),
    )


class WaterReading(Base):
    __tablename__ = "water_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    liters = Column(Float, nullable=False)
    source = Column(String, nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index('ix_water_readings_user_recorded', 'user_id', 'recorded_at'),
    )
