from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)
    url = Column(String, unique=True)
    status = Column(String, default="new")  # new, viewed, applied, expired
    posted_date = Column(Date)
    expires_date = Column(Date)
    scanned_at = Column(DateTime, default=datetime.utcnow)

    domain = relationship("Domain", back_populates="jobs")
    institution = relationship("Institution", back_populates="jobs")
    resumes = relationship("Resume", back_populates="job")
    applications = relationship("Application", back_populates="job")


class ScanHistory(Base):
    __tablename__ = "scan_history"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    scan_time = Column(DateTime, default=datetime.utcnow)
    jobs_found = Column(Integer, default=0)
    jobs_new = Column(Integer, default=0)
    status = Column(String, default="success")

    domain = relationship("Domain", back_populates="scan_history")
