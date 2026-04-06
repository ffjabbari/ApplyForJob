from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models.institution import Institution
from backend.models.domain import Domain

router = APIRouter(prefix="/api/institutions", tags=["institutions"])

class InstitutionCreate(BaseModel):
    name: str
    website: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = None

class InstitutionOut(BaseModel):
    id: int
    domain_id: int
    name: str
    website: Optional[str]
    location: Optional[str]
    type: Optional[str]
    is_favorite: bool
    class Config: from_attributes = True

@router.get("/", response_model=list[InstitutionOut])
def list_institutions(db: Session = Depends(get_db)):
    active = db.query(Domain).filter(Domain.is_active == True).first()
    q = db.query(Institution)
    if active:
        q = q.filter(Institution.domain_id == active.id)
    return q.all()

@router.post("/", response_model=InstitutionOut)
def create_institution(data: InstitutionCreate, db: Session = Depends(get_db)):
    active = db.query(Domain).filter(Domain.is_active == True).first()
    if not active:
        raise HTTPException(status_code=400, detail="No active domain")
    inst = Institution(domain_id=active.id, **data.model_dump())
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst

@router.put("/{id}/favorite", response_model=InstitutionOut)
def toggle_favorite(id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    inst.is_favorite = not inst.is_favorite
    db.commit()
    db.refresh(inst)
    return inst

@router.delete("/{id}")
def delete_institution(id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(inst)
    db.commit()
    return {"ok": True}
