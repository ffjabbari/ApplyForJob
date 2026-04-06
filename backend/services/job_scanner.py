"""
Job Scanner Service — scrapes job boards and stores results in DB.
Triggered by APScheduler daily or manually via POST /api/jobs/scan
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.job import Job, ScanHistory
from backend.models.domain import Domain


async def scrape_jobs_for_domain(domain_name: str) -> list[dict]:
    """
    Placeholder scraper — replace with real Playwright/BeautifulSoup scrapers.
    Returns a list of raw job dicts.
    """
    # TODO: import and call scrapers/linkedin.py, scrapers/indeed.py, etc.
    return []


def run_scan(db: Session):
    """Run a full scan for all active domains."""
    domains = db.query(Domain).filter(Domain.is_active == True).all()
    for domain in domains:
        _scan_domain(domain, db)


def _scan_domain(domain: Domain, db: Session):
    import asyncio
    raw_jobs = asyncio.run(scrape_jobs_for_domain(domain.name))
    new_count = 0

    for raw in raw_jobs:
        # Deduplicate by URL
        existing = db.query(Job).filter(Job.url == raw.get("url")).first()
        if existing:
            continue
        job = Job(
            domain_id=domain.id,
            title=raw.get("title", ""),
            description=raw.get("description", ""),
            location=raw.get("location", ""),
            url=raw.get("url", ""),
            posted_date=raw.get("posted_date"),
            status="new",
            scanned_at=datetime.utcnow(),
        )
        db.add(job)
        new_count += 1

    db.commit()

    history = ScanHistory(
        domain_id=domain.id,
        jobs_found=len(raw_jobs),
        jobs_new=new_count,
        status="success",
    )
    db.add(history)
    db.commit()
