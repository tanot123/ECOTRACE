import hashlib
import json
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.models.scan import ScanResult
from app.services.gemini_service import GeminiService
from uuid import UUID

class ScanService:
    @staticmethod
    def _hash_image(image_bytes: bytes) -> str:
        return hashlib.sha256(image_bytes).hexdigest()

    @staticmethod
    async def process_scan(db: AsyncSession, user_id: UUID, image_bytes: bytes, scan_type: str, mime_type: str = "image/jpeg") -> ScanResult:
        image_hash = ScanService._hash_image(image_bytes)

        # Check Cache (only cache packaging and barcode, receipts are usually unique but we'll cache to save quota anyway if same image)
        cached_result = await db.execute(
            select(ScanResult)
            .where(ScanResult.image_hash == image_hash, ScanResult.scan_type == scan_type)
            .order_by(desc(ScanResult.scanned_at))
            .limit(1)
        )
        cached = cached_result.scalars().first()
        if cached and cached.status == "success":
            return cached

        # Call Gemini
        start_time = time.time()
        try:
            analysis = await GeminiService.analyze_image(image_bytes, scan_type, mime_type)
            status = "error" if analysis.get("error") else "success"
        except Exception as e:
            analysis = {"error": "API_ERROR", "message": str(e)}
            status = "error"
        processing_time = int((time.time() - start_time) * 1000)

        # Store Result
        scan_record = ScanResult(
            user_id=user_id,
            scan_type=scan_type,
            image_hash=image_hash,
            analysis_result=analysis,
            raw_response=json.dumps(analysis),
            processing_time_ms=processing_time,
            gemini_model="gemini-2.5-flash",
            status=status
        )
        db.add(scan_record)
        await db.commit()
        await db.refresh(scan_record)
        
        return scan_record

    @staticmethod
    async def get_history(db: AsyncSession, user_id: UUID, limit: int = 10) -> list[ScanResult]:
        result = await db.execute(
            select(ScanResult)
            .where(ScanResult.user_id == user_id)
            .order_by(desc(ScanResult.scanned_at))
            .limit(limit)
        )
        return result.scalars().all()
