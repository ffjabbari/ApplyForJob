from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models.domain import Domain

router = APIRouter(prefix="/api/domains", tags=["domains"])

class DomainCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DomainOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    class Config: from_attributes = True

@router.get("/", response_model=list[DomainOut])
def list_domains(db: Session = Depends(get_db)):
    return db.query(Domain).all()

@router.post("/", response_model=DomainOut)
def create_domain(data: DomainCreate, db: Session = Depends(get_db)):
    domain = Domain(**data.model_dump())
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain

@router.put("/{id}/activate", response_model=DomainOut)
def activate_domain(id: int, db: Session = Depends(get_db)):
    db.query(Domain).update({"is_active": False})
    domain = db.query(Domain).filter(Domain.id == id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain.is_active = True
    db.commit()
    db.refresh(domain)
    return domain

@router.delete("/{id}")
def delete_domain(id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    db.delete(domain)
    db.commit()
    return {"ok": True}
