from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models.user import User, ProfileSkill, ProfileExperience

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class SkillCreate(BaseModel):
    skill: str
    level: Optional[str] = None

class ExperienceCreate(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class ProfileOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    bio: Optional[str]
    class Config: from_attributes = True

@router.get("/", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user

@router.put("/", response_model=ProfileOut)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user

@router.get("/skills")
def get_skills(db: Session = Depends(get_db)):
    return db.query(ProfileSkill).filter(ProfileSkill.user_id == 1).all()

@router.post("/skills")
def add_skill(data: SkillCreate, db: Session = Depends(get_db)):
    skill = ProfileSkill(user_id=1, **data.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

@router.delete("/skills/{id}")
def delete_skill(id: int, db: Session = Depends(get_db)):
    skill = db.query(ProfileSkill).filter(ProfileSkill.id == id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"ok": True}

@router.get("/experience")
def get_experience(db: Session = Depends(get_db)):
    return db.query(ProfileExperience).filter(ProfileExperience.user_id == 1).all()

@router.post("/experience")
def add_experience(data: ExperienceCreate, db: Session = Depends(get_db)):
    exp = ProfileExperience(user_id=1, **data.model_dump())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp
