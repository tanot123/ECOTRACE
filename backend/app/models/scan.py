from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_type = Column(String, nullable=False)
    image_hash = Column(String, nullable=False, index=True)
    analysis_result = Column(JSONB, nullable=False)
    raw_response = Column(String, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    gemini_model = Column(String, nullable=True)
    status = Column(String, nullable=False, default="success") # success, partial, error
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())
