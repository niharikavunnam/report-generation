import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.models.database_models import AnalysisRecord, SessionLocal, User

router = APIRouter(tags=["report"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/report/{analysis_id}")
def get_report(analysis_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id, AnalysisRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "analysis_id": record.id,
        "filename": record.filename,
        "body_region": record.body_region,
        "xray_type": record.xray_type,
        "diagnosis": record.diagnosis,
        "confidence": record.confidence,
        "report": record.report_text,
        "findings": json.loads(record.findings),
    }
