from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.services import agent as agent_svc
from backend.models.interview import ResumeTemplate, InterviewSession, InterviewMessage

router = APIRouter(prefix="/api/agent", tags=["agent"])


class StartSession(BaseModel):
    template_id: Optional[int] = None


class SendMessage(BaseModel):
    message: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    discoveries_json: Optional[str]
    class Config: from_attributes = True


class SessionOut(BaseModel):
    id: int
    status: str
    template_id: Optional[int]
    class Config: from_attributes = True


@router.post("/start", response_model=SessionOut)
def start_session(data: StartSession, db: Session = Depends(get_db)):
    session = agent_svc.create_session(data.template_id, db)
    return session


@router.post("/{session_id}/message")
async def send_message(session_id: int, data: SendMessage, db: Session = Depends(get_db)):
    result = await agent_svc.chat(session_id, data.message, db)
    return result


@router.get("/{session_id}/history", response_model=list[MessageOut])
def get_history(session_id: int, db: Session = Depends(get_db)):
    return agent_svc.get_session_history(session_id, db)


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(InterviewSession).order_by(InterviewSession.started_at.desc()).all()


@router.get("/templates")
def list_templates(db: Session = Depends(get_db)):
    return db.query(ResumeTemplate).all()
