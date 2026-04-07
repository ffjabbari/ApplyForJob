"""
Job Finder Agent Service
GPT-4o-mini with function-calling tools that ARE the system's own APIs.
"""
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.interview import InterviewSession, InterviewMessage, ResumeTemplate
from backend.models.user import User, ProfileSkill, ProfileExperience
from backend.models.institution import Institution
from backend.models.job import Job
from backend.models.domain import Domain

# ── Tool definitions for GPT function-calling ──────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for job postings or institutions matching a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "search_type": {"type": "string", "enum": ["jobs", "institutions"], "description": "What to search for"}
                },
                "required": ["query", "search_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_institution",
            "description": "Add a discovered institution to the user's system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "website": {"type": "string"},
                    "location": {"type": "string"},
                    "type": {"type": "string", "description": "e.g. University, Bank, Tech Company"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_job",
            "description": "Add a discovered job posting to the user's job board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "location": {"type": "string"},
                    "url": {"type": "string"},
                    "institution_name": {"type": "string"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_profile",
            "description": "Update the user's profile with skills or bio extracted from the conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bio": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "object", "properties": {"skill": {"type": "string"}, "level": {"type": "string"}}}
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_resume",
            "description": "Build a tailored resume for a specific job using GPT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "integer", "description": "ID of the job to build resume for"}
                },
                "required": ["job_id"]
            }
        }
    }
]

# ── System prompt ───────────────────────────────────────────────────────────

BASE_SYSTEM_PROMPT = """You are the Job Finder Agent for JobHunter AI — a personal assistant that helps Fred F. Jabbari find and apply for jobs.

Your job is to:
1. Interview the user conversationally to understand what jobs they want
2. Use your tools to search the web for matching jobs and institutions
3. Automatically add discovered institutions and jobs to the system
4. Extract skills and experience from the conversation and update the profile
5. Build tailored resumes for discovered jobs
6. Keep the user informed of every action you take

Guidelines:
- Be warm, professional, and encouraging
- After each user answer, call relevant tools immediately — don't wait
- Show what you found and what you added in a clear, readable way
- Ask one focused question at a time
- When you find institutions or jobs, tell the user what you found and confirm you added them
- Use bullet points for lists of discoveries
- After gathering enough info (3-4 exchanges), offer to build resumes for the queued jobs

Start by asking what type of position they're looking for."""


# ── Tool execution ──────────────────────────────────────────────────────────

async def execute_tool(tool_name: str, args: dict, db: Session) -> dict:
    """Execute a tool call and return the result."""

    if tool_name == "search_web":
        return await _search_web(args["query"], args.get("search_type", "jobs"))

    elif tool_name == "add_institution":
        return _add_institution(args, db)

    elif tool_name == "add_job":
        return _add_job(args, db)

    elif tool_name == "update_profile":
        return _update_profile(args, db)

    elif tool_name == "build_resume":
        return await _build_resume(args["job_id"], db)

    return {"error": f"Unknown tool: {tool_name}"}


async def _search_web(query: str, search_type: str) -> dict:
    """Search via Tavily API or fall back to mock results."""
    tavily_key = os.getenv("TAVILY_API_KEY", "")

    if tavily_key:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": tavily_key, "query": query, "max_results": 5},
                    timeout=10
                )
                data = resp.json()
                results = [{"title": r.get("title"), "url": r.get("url"), "snippet": r.get("content", "")[:200]}
                           for r in data.get("results", [])]
                return {"results": results, "source": "tavily"}
        except Exception as e:
            print(f"Tavily error: {e}")

    # Fallback: return plausible mock results based on query
    return _mock_search(query, search_type)


def _mock_search(query: str, search_type: str) -> dict:
    q = query.lower()
    if search_type == "institutions":
        results = []
        if any(w in q for w in ["university", "college", "academic", "teach", "professor", "lecturer"]):
            results = [
                {"title": "Washington University in St. Louis", "url": "https://wustl.edu/careers", "snippet": "Top research university in St. Louis hiring adjunct faculty in CS and Finance."},
                {"title": "University of Missouri - St. Louis (UMSL)", "url": "https://www.umsl.edu/jobs", "snippet": "UMSL hiring part-time instructors in Computer Science and Business."},
                {"title": "Saint Louis University (SLU)", "url": "https://www.slu.edu/jobs", "snippet": "SLU School of Engineering seeking adjunct faculty for AI and software courses."},
                {"title": "UCLA Extension", "url": "https://extension.ucla.edu", "snippet": "UCLA Extension offers remote adjunct positions in technology and business."},
            ]
        elif any(w in q for w in ["bank", "finance", "financial"]):
            results = [
                {"title": "Edward Jones", "url": "https://careers.edwardjones.com", "snippet": "Edward Jones HQ in St. Louis — hiring finance professionals."},
                {"title": "Centene Corporation", "url": "https://careers.centene.com", "snippet": "Fortune 500 in St. Louis hiring finance and tech roles."},
            ]
        else:
            results = [{"title": f"Institution matching '{query}'", "url": "https://example.com", "snippet": "Relevant institution found."}]
    else:
        results = []
        if any(w in q for w in ["cs", "computer science", "software", "programming", "adjunct"]):
            results = [
                {"title": "Adjunct Instructor — Computer Science", "url": "https://higheredjobs.com/mock/cs1", "snippet": "Teach intro programming and software engineering. Python/Java required. St. Louis area."},
                {"title": "Part-Time Lecturer — AI & Machine Learning", "url": "https://higheredjobs.com/mock/ai1", "snippet": "Deliver AI fundamentals course. Industry experience preferred. Remote option available."},
            ]
        elif any(w in q for w in ["finance", "mba", "business", "accounting"]):
            results = [
                {"title": "Adjunct Professor — Finance", "url": "https://higheredjobs.com/mock/fin1", "snippet": "Teach corporate finance and investments. CFA or MBA preferred."},
            ]
        else:
            results = [{"title": f"Job matching '{query}'", "url": "https://example.com/job", "snippet": "Relevant position found."}]

    return {"results": results, "source": "mock"}


def _add_institution(args: dict, db: Session) -> dict:
    active_domain = db.query(Domain).filter(Domain.is_active == True).first()
    domain_id = active_domain.id if active_domain else 1

    existing = db.query(Institution).filter(Institution.name == args["name"]).first()
    if existing:
        return {"status": "already_exists", "institution_id": existing.id, "name": args["name"]}

    inst = Institution(
        domain_id=domain_id,
        name=args["name"],
        website=args.get("website", ""),
        location=args.get("location", ""),
        type=args.get("type", ""),
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return {"status": "added", "institution_id": inst.id, "name": inst.name}


def _add_job(args: dict, db: Session) -> dict:
    active_domain = db.query(Domain).filter(Domain.is_active == True).first()
    domain_id = active_domain.id if active_domain else 1

    url = args.get("url", f"https://jobhunter.local/job/{args['title'].replace(' ', '-')}")
    existing = db.query(Job).filter(Job.url == url).first()
    if existing:
        return {"status": "already_exists", "job_id": existing.id, "title": args["title"]}

    # Try to find institution by name
    institution_id = None
    if args.get("institution_name"):
        inst = db.query(Institution).filter(Institution.name.ilike(f"%{args['institution_name']}%")).first()
        if inst:
            institution_id = inst.id

    job = Job(
        domain_id=domain_id,
        institution_id=institution_id,
        title=args["title"],
        description=args.get("description", ""),
        location=args.get("location", ""),
        url=url,
        status="new",
        scanned_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"status": "added", "job_id": job.id, "title": job.title}


def _update_profile(args: dict, db: Session) -> dict:
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        return {"error": "User not found"}

    if args.get("bio"):
        user.bio = args["bio"]

    added_skills = []
    for s in args.get("skills", []):
        skill_name = s.get("skill", "")
        if not skill_name:
            continue
        existing = db.query(ProfileSkill).filter(
            ProfileSkill.user_id == 1,
            ProfileSkill.skill.ilike(skill_name)
        ).first()
        if not existing:
            db.add(ProfileSkill(user_id=1, skill=skill_name, level=s.get("level", "")))
            added_skills.append(skill_name)

    db.commit()
    return {"status": "updated", "skills_added": added_skills}


async def _build_resume(job_id: int, db: Session) -> dict:
    try:
        from backend.services.resume_builder import build
        resume = await build(job_id, 1, db)
        return {"status": "built", "resume_id": resume.id, "job_id": job_id}
    except Exception as e:
        return {"error": str(e)}


# ── Main agent chat function ────────────────────────────────────────────────

async def chat(session_id: int, user_message: str, db: Session) -> dict:
    """
    Process a user message in an interview session.
    Returns: { reply, discoveries, actions_taken }
    """
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}

    # Save user message
    db.add(InterviewMessage(session_id=session_id, role="user", content=user_message))
    db.commit()

    # Build message history for GPT
    history = db.query(InterviewMessage).filter(
        InterviewMessage.session_id == session_id,
        InterviewMessage.role.in_(["user", "assistant"])
    ).order_by(InterviewMessage.id).all()

    messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
    for m in history:
        messages.append({"role": m.role, "content": m.content})

    discoveries = []
    actions_taken = []

    # Agentic loop — keep calling GPT until no more tool calls
    max_iterations = 5
    for _ in range(max_iterations):
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        # No tool calls — we have the final reply
        if not msg.tool_calls:
            reply = msg.content or ""
            db.add(InterviewMessage(session_id=session_id, role="assistant", content=reply,
                                    discoveries_json=json.dumps(discoveries)))
            db.commit()
            return {"reply": reply, "discoveries": discoveries, "actions_taken": actions_taken}

        # Process tool calls
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]})

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            result = await execute_tool(tool_name, args, db)
            actions_taken.append({"tool": tool_name, "args": args, "result": result})

            # Track discoveries
            if tool_name == "add_institution" and result.get("status") == "added":
                discoveries.append({"type": "institution", "name": result["name"], "id": result["institution_id"]})
            elif tool_name == "add_job" and result.get("status") == "added":
                discoveries.append({"type": "job", "title": result["title"], "id": result["job_id"]})
            elif tool_name == "build_resume" and result.get("status") == "built":
                discoveries.append({"type": "resume", "resume_id": result["resume_id"], "job_id": result["job_id"]})

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })

    # Fallback if loop exhausted
    return {"reply": "I've processed your request and updated your system.", "discoveries": discoveries, "actions_taken": actions_taken}


# ── Session management ──────────────────────────────────────────────────────

def create_session(template_id: int | None, db: Session) -> InterviewSession:
    session = InterviewSession(user_id=1, template_id=template_id, status="active")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_history(session_id: int, db: Session) -> list:
    return db.query(InterviewMessage).filter(
        InterviewMessage.session_id == session_id
    ).order_by(InterviewMessage.id).all()
