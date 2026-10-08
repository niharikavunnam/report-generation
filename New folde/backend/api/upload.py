import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.models.database_models import AnalysisRecord, SessionLocal
from backend.services.abnormality_detector import detect_abnormalities
from backend.services.explainability import generate_explainability
from backend.services.feature_extractor import extract_image_features
from backend.services.image_classifier import classify_xray
from backend.services.image_preprocessing import preprocess_image
from backend.services.report_generator import generate_report

router = APIRouter(tags=["upload"])
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dicom"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/upload")
async def upload_xray(
    file: UploadFile = File(...),
    body_region: str = Form(...),
    xray_type: str | None = Form(None),
    patient_name: str | None = Form(None),
    patient_id: str | None = Form(None),
    patient_age: str | None = Form(None),
    clinical_notes: str | None = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use JPG, JPEG, PNG, or DICOM.")

    file_bytes = await file.read()
    if not file_bytes or len(file_bytes) < 10:
        raise HTTPException(status_code=400, detail="Uploaded file is empty or corrupted")

    safe_name = f"{uuid.uuid4().hex}{ext}"
    upload_path = UPLOAD_DIR / safe_name
    upload_path.write_bytes(file_bytes)

    preprocessing = preprocess_image(str(upload_path))
    classification = classify_xray(body_region=body_region, xray_type=xray_type)
    features = extract_image_features(str(upload_path))
    findings = detect_abnormalities(body_region=body_region, xray_type=xray_type, classification=classification)
    explanation = generate_explainability(findings)
    report = generate_report(classification, findings, patient_info={
        "patient_name": patient_name,
        "patient_id": patient_id,
        "patient_age": patient_age,
        "clinical_notes": clinical_notes,
    })

    summary = findings[0]["name"] if findings else "No significant abnormality detected"
    record = AnalysisRecord(
        user_id=current_user.id,
        filename=safe_name,
        body_region=body_region,
        xray_type=xray_type,
        patient_info=json.dumps({
            "patient_name": patient_name,
            "patient_id": patient_id,
            "patient_age": patient_age,
            "clinical_notes": clinical_notes,
        }),
        findings=json.dumps(findings),
        diagnosis=summary,
        report_text=report,
        confidence=f"{classification['confidence'] * 100:.1f}%",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "analysis_id": record.id,
        "body_region": body_region,
        "xray_type": xray_type,
        "diagnosis": summary,
        "confidence": record.confidence,
        "report": report,
        "preprocessing": preprocessing,
        "features": features,
        "explanation": explanation,
    }
