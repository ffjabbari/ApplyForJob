from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.database import get_db
from backend.models.application import Application

router = APIRouter(prefix="/api/applications", tags=["applications"])

class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    method: Optional[str] = "email"
    notes: Optional[str] = None
    user_id: int = 1

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationOut(BaseModel):
    id: int
    user_id: int
    job_id: int
    resume_id: Optional[int]
    status: str
    method: Optional[str]
    applied_at: datetime
    notes: Optional[str]
    class Config: from_attributes = True

@router.get("/", response_model=list[ApplicationOut])
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.applied_at.desc()).all()

@router.post("/", response_model=ApplicationOut)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@router.put("/{id}", response_model=ApplicationOut)
def update_application(id: int, data: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(app, k, v)
    db.commit()
    db.refresh(app)
    return app
