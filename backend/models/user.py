from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user")
    applications = relationship("Application", back_populates="user")
    skills = relationship("ProfileSkill", back_populates="user")
    experiences = relationship("ProfileExperience", back_populates="user")


class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill = Column(String, nullable=False)
    level = Column(String)

    user = relationship("User", back_populates="skills")


class ProfileExperience(Base):
    __tablename__ = "profile_experience"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String)
    title = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    description = Column(Text)

    user = relationship("User", back_populates="experiences")
