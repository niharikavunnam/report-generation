import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.models.database_models import Base, engine
from backend.api.auth import router as auth_router
from backend.api.upload import router as upload_router
from backend.api.analysis import router as analysis_router
from backend.api.report import router as report_router
from backend.api.history import router as history_router

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

os.makedirs(BASE_DIR / "data", exist_ok=True)
os.makedirs(BASE_DIR / "uploads", exist_ok=True)

app = FastAPI(title="Automated Multi-Modal Medical Report Generation", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Must be registered before static mount to avoid route conflicts.
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(report_router)
app.include_router(history_router)


@app.on_event("startup")
def startup_event():
    os.makedirs(BASE_DIR / "data", exist_ok=True)
    os.makedirs(BASE_DIR / "uploads", exist_ok=True)
    Base.metadata.create_all(bind=engine)


@app.get("/api")
def api_root():
    return {"message": "Medical imaging report generation API is running.", "status": "ok"}


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
