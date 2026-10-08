from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.models.database_models import AnalysisRecord, SessionLocal, User

router = APIRouter(tags=["history"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).filter(AnalysisRecord.user_id == current_user.id).order_by(AnalysisRecord.created_at.desc()).all()
    history = []
    for record in records:
        history.append({
            "id": record.id,
            "filename": record.filename,
            "body_region": record.body_region,
            "xray_type": record.xray_type,
            "diagnosis": record.diagnosis,
            "confidence": record.confidence,
            "created_at": record.created_at.isoformat(),
        })
    return history
