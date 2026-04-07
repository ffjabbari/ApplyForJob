from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class ResumeTemplate(Base):
    __tablename__ = "resume_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    questions_json = Column(Text)   # JSON list of question strings
    system_prompt = Column(Text)    # Agent system prompt for this template
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("InterviewSession", back_populates="template")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("resume_templates.id"), nullable=True)
    status = Column(String, default="active")  # active, completed, abandoned
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    template = relationship("ResumeTemplate", back_populates="sessions")
    messages = relationship("InterviewMessage", back_populates="session", order_by="InterviewMessage.id")


class InterviewMessage(Base):
    __tablename__ = "interview_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    role = Column(String, nullable=False)   # user | assistant | tool
    content = Column(Text, nullable=False)
    discoveries_json = Column(Text, nullable=True)  # JSON: institutions/jobs found
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="messages")
