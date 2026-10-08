from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class TokenPayload(BaseModel):
    sub: int
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class UploadAnalysisRequest(BaseModel):
    body_region: str
    xray_type: Optional[str] = None
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    patient_age: Optional[str] = None
    clinical_notes: Optional[str] = None


class UploadResponse(BaseModel):
    analysis_id: int
    body_region: str
    xray_type: Optional[str]
    diagnosis: str
    confidence: str
    report: str


class AnalysisSummary(BaseModel):
    id: int
    filename: str
    body_region: str
    xray_type: Optional[str]
    diagnosis: str
    confidence: str
    created_at: str
