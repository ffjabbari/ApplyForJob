from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models.resume import Resume

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

class ResumeBuildRequest(BaseModel):
    job_id: int
    user_id: int = 1  # single-user system

class ResumeOut(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int]
    version: str
    content_json: Optional[str]
    pdf_path: Optional[str]
    docx_path: Optional[str]
    class Config: from_attributes = True

@router.get("/", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db)):
    return db.query(Resume).order_by(Resume.created_at.desc()).all()

@router.get("/{id}", response_model=ResumeOut)
def get_resume(id: int, db: Session = Depends(get_db)):
    r = db.query(Resume).filter(Resume.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    return r

@router.post("/build", response_model=ResumeOut)
async def build_resume(req: ResumeBuildRequest, db: Session = Depends(get_db)):
    from backend.services.resume_builder import build
    resume = await build(req.job_id, req.user_id, db)
    return resume

@router.get("/{id}/pdf")
def download_pdf(id: int, db: Session = Depends(get_db)):
    r = db.query(Resume).filter(Resume.id == id).first()
    if not r or not r.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(r.pdf_path, media_type="application/pdf", filename=f"resume_{id}.pdf")

@router.get("/{id}/docx")
def download_docx(id: int, db: Session = Depends(get_db)):
    r = db.query(Resume).filter(Resume.id == id).first()
    if not r or not r.docx_path:
        raise HTTPException(status_code=404, detail="DOCX not found")
    return FileResponse(r.docx_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=f"resume_{id}.docx")
