"""
APScheduler setup — runs daily job scans automatically.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.database import SessionLocal
from backend.services.job_scanner import run_scan

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        _scheduled_scan,
        trigger=CronTrigger(hour=7, minute=0),  # 7:00 AM daily
        id="daily_job_scan",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started — daily scan at 7:00 AM")


def stop_scheduler():
    scheduler.shutdown()


def _scheduled_scan():
    db = SessionLocal()
    try:
        run_scan(db)
    finally:
        db.close()
