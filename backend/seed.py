"""
Seed script — creates initial user and domains.
Run once: python -m backend.seed
"""
from backend.database import init_db, SessionLocal
from backend.models.user import User
from backend.models.domain import Domain

def seed():
    init_db()
    db = SessionLocal()

    # Create default user if not exists
    if not db.query(User).filter(User.id == 1).first():
        user = User(
            id=1,
            name="Fred F. Jabbari",
            email="fred@example.com",
            phone="314-555-0100",
            bio="Software engineer and finance professional based in St. Louis, MO. "
                "Background in software development, finance, and real estate.",
        )
        db.add(user)

    # Create default domains
    default_domains = [
        ("University", "Part-time teaching and academic positions", True),
        ("Bank", "Banking and financial institutions", False),
        ("Insurance", "Insurance companies", False),
        ("Pharma", "Pharmaceutical and biotech companies", False),
        ("Tech", "Technology companies", False),
        ("Other", "Other industries", False),
    ]

    for name, desc, active in default_domains:
        if not db.query(Domain).filter(Domain.name == name).first():
            db.add(Domain(name=name, description=desc, is_active=active))

    db.commit()
    db.close()
    print("Seed complete.")

if __name__ == "__main__":
    seed()
