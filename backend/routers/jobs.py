from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from backend.database import get_db
from backend.models.job import Job, ScanHistory
from backend.models.domain import Domain

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

class JobOut(BaseModel):
    id: int
    domain_id: int
    institution_id: Optional[int]
    title: str
    description: Optional[str]
    location: Optional[str]
    url: Optional[str]
    status: str
    posted_date: Optional[date]
    scanned_at: datetime
    class Config: from_attributes = True

@router.get("/", response_model=list[JobOut])
def list_jobs(status: Optional[str] = None, db: Session = Depends(get_db)):
    active = db.query(Domain).filter(Domain.is_active == True).first()
    q = db.query(Job)
    if active:
        q = q.filter(Job.domain_id == active.id)
    if status:
        q = q.filter(Job.status == status)
    return q.order_by(Job.scanned_at.desc()).all()

@router.get("/new", response_model=list[JobOut])
def new_jobs(db: Session = Depends(get_db)):
    active = db.query(Domain).filter(Domain.is_active == True).first()
    q = db.query(Job).filter(Job.status == "new")
    if active:
        q = q.filter(Job.domain_id == active.id)
    return q.all()

@router.get("/{id}", response_model=JobOut)
def get_job(id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/scan")
def trigger_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from backend.services.job_scanner import run_scan
    background_tasks.add_task(run_scan, db)
    return {"message": "Scan started"}

@router.put("/{id}/status")
def update_status(id: int, status: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = status
    db.commit()
    return {"ok": True}
