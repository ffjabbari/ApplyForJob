from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_db
from backend.services.scheduler import start_scheduler, stop_scheduler
from backend.routers import domains, jobs, institutions, resumes, applications, profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="JobHunter AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(domains.router)
app.include_router(jobs.router)
app.include_router(institutions.router)
app.include_router(resumes.router)
app.include_router(applications.router)
app.include_router(profile.router)


@app.get("/")
def root():
    return {"message": "JobHunter AI API", "docs": "/docs"}
