# 🤖 JobHunter AI

Intelligent Job Search, Resume Building & Auto-Apply System.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
python -m backend.seed          # create DB + seed user/domains
uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

- Backend API: http://localhost:8000 (Swagger: /docs)
- Frontend: http://localhost:5173
- Docs portal: open Docs/index.html

## Environment Variables
```
OPENAI_API_KEY=sk-...       # optional, falls back to stub
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=yourpassword
DATABASE_URL=sqlite:///./data/jobhunter.db
```

## Architecture
See `Docs/index.html` for full architecture, data flow, and API reference.
