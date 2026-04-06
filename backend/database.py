from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Always resolve data/ relative to the project root (parent of this file's directory)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
os.makedirs(_DATA_DIR, exist_ok=True)

_DEFAULT_DB = f"sqlite:///{os.path.join(_DATA_DIR, 'jobhunter.db')}"
DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_DB)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.models import user, domain, institution, job, resume, application
    Base.metadata.create_all(bind=engine)
