"""
Seed sample job postings for testing.
Run: python -m backend.seed_jobs
"""
from datetime import date
from backend.database import init_db, SessionLocal
from backend.models.job import Job
from backend.models.domain import Domain

SAMPLE_JOBS = [
    {
        "title": "Adjunct Instructor — Computer Science",
        "description": "Teach introductory programming courses (Python, Java) to undergraduate students. "
                       "Evening and weekend sections available. MS or PhD in CS or related field preferred.",
        "location": "St. Louis, MO",
        "url": "https://higheredjobs.com/sample/1001",
        "posted_date": date(2026, 3, 20),
    },
    {
        "title": "Part-Time Lecturer — Finance",
        "description": "Deliver undergraduate finance courses including Corporate Finance and Investments. "
                       "CFA or MBA preferred. Industry experience welcome.",
        "location": "St. Louis, MO (Hybrid)",
        "url": "https://higheredjobs.com/sample/1002",
        "posted_date": date(2026, 3, 22),
    },
    {
        "title": "Adjunct Faculty — Software Engineering",
        "description": "Teach software engineering principles, agile methodologies, and system design. "
                       "Industry experience in software development required.",
        "location": "Remote",
        "url": "https://higheredjobs.com/sample/1003",
        "posted_date": date(2026, 3, 25),
    },
    {
        "title": "Part-Time Instructor — Data Science",
        "description": "Teach data science fundamentals, machine learning basics, and Python for data analysis. "
                       "Experience with pandas, scikit-learn, and Jupyter required.",
        "location": "St. Louis, MO",
        "url": "https://higheredjobs.com/sample/1004",
        "posted_date": date(2026, 3, 28),
    },
    {
        "title": "Adjunct Professor — Real Estate Finance",
        "description": "Teach real estate investment analysis, property valuation, and real estate markets. "
                       "Active real estate license or industry background strongly preferred.",
        "location": "St. Louis, MO",
        "url": "https://higheredjobs.com/sample/1005",
        "posted_date": date(2026, 4, 1),
    },
    {
        "title": "Visiting Lecturer — Business Analytics",
        "description": "Deliver courses in business analytics, SQL, and data visualization tools (Tableau, Power BI). "
                       "MBA or MS in Analytics preferred.",
        "location": "Online",
        "url": "https://higheredjobs.com/sample/1006",
        "posted_date": date(2026, 4, 2),
    },
]


def seed_jobs():
    init_db()
    db = SessionLocal()

    domain = db.query(Domain).filter(Domain.name == "University").first()
    if not domain:
        print("University domain not found. Run python -m backend.seed first.")
        db.close()
        return

    added = 0
    for j in SAMPLE_JOBS:
        if db.query(Job).filter(Job.url == j["url"]).first():
            continue
        db.add(Job(domain_id=domain.id, status="new", **j))
        added += 1

    db.commit()
    db.close()
    print(f"Seeded {added} sample jobs.")


if __name__ == "__main__":
    seed_jobs()
