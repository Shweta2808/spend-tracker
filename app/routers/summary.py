from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app import schemas
from app.auth import require_api_key
from app.dependencies import get_summary_service
from app.summary_service import SummaryService

router = APIRouter(tags=["summary"], dependencies=[Depends(require_api_key)])


@router.get("/summary", response_model=schemas.SummaryOut)
def get_summary(
    month: Optional[str] = Query(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    summary_service: SummaryService = Depends(get_summary_service),
):
    resolved_month = month or datetime.now(timezone.utc).strftime("%Y-%m")
    return summary_service.build(resolved_month)
