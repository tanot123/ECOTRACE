from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID

class ScanResultResponse(BaseModel):
    id: UUID
    scan_type: str
    status: str
    analysis: Dict[str, Any]
    image_thumbnail_url: Optional[str] = None
    scanned_at: datetime
    processing_time_ms: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
