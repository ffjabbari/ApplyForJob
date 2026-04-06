"""
Auto-Apply Service — submits job applications via email, web form, or portal.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from sqlalchemy.orm import Session
from backend.models.application import Application
from backend.models.job import Job
from backend.models.resume import Resume

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def submit_application(application_id: int, db: Session):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        return {"error": "Application not found"}

    job = db.query(Job).filter(Job.id == app.job_id).first()
    resume = db.query(Resume).filter(Resume.id == app.resume_id).first() if app.resume_id else None

    if app.method == "email":
        result = _send_email(job, resume)
    elif app.method == "web_form":
        result = _fill_web_form(job, resume)
    else:
        result = {"status": "portal", "url": job.url}

    if result.get("status") != "error":
        app.status = "submitted"
        db.commit()

    return result


def _send_email(job: Job, resume: Resume) -> dict:
    if not SMTP_USER:
        return {"status": "skipped", "reason": "SMTP not configured"}
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = "hiring@institution.com"  # TODO: pull from institution record
        msg["Subject"] = f"Application for {job.title}"
        msg.attach(MIMEText(f"Please find my application for {job.title} attached.", "plain"))

        if resume and resume.pdf_path:
            with open(resume.pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename=resume.pdf")
                msg.attach(part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def _fill_web_form(job: Job, resume: Resume) -> dict:
    # TODO: implement Playwright form filling
    return {"status": "pending", "reason": "Web form automation not yet implemented"}
