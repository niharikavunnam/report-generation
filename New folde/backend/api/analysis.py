import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.models.database_models import AnalysisRecord, SessionLocal, User

router = APIRouter(tags=["analysis"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/analysis")
def list_analyses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).filter(AnalysisRecord.user_id == current_user.id).order_by(AnalysisRecord.created_at.desc()).all()
    results = []
    for record in records:
        results.append({
            "id": record.id,
            "filename": record.filename,
            "body_region": record.body_region,
            "xray_type": record.xray_type,
            "diagnosis": record.diagnosis,
            "confidence": record.confidence,
            "created_at": record.created_at.isoformat(),
            "findings": json.loads(record.findings),
        })
    return results


@router.get("/api/analysis/{analysis_id}")
def get_analysis(analysis_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id, AnalysisRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found")

    return {
        "id": record.id,
        "filename": record.filename,
        "body_region": record.body_region,
        "xray_type": record.xray_type,
        "patient_info": json.loads(record.patient_info) if record.patient_info else {},
        "diagnosis": record.diagnosis,
        "confidence": record.confidence,
        "findings": json.loads(record.findings),
        "report_text": record.report_text,
        "created_at": record.created_at.isoformat(),
    }
