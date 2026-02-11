from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from redis import Redis


APP_NAME = "resume-ops-api"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = "applications:queue"

app = FastAPI(title=APP_NAME)


class CandidateProfile(BaseModel):
    full_name: str
    email: str
    title: str
    summary: str
    skills: list[str]
    experience: list[str]
    preferred_roles: list[str] = Field(default_factory=list)


class ResumeRequest(BaseModel):
    profile: CandidateProfile
    target_role: str
    target_company: str
    keywords: list[str] = Field(default_factory=list)


class ResumeResponse(BaseModel):
    resume_id: str
    generated_at: datetime
    content: str


class Job(BaseModel):
    company: str
    role: str
    location: str
    description: str
    apply_url: str


class AutoApplyRequest(BaseModel):
    resume_id: str
    resume_text: str
    jobs: list[Job]
    auto_submit: bool = True


class QueueResult(BaseModel):
    queued: int
    queue_key: str


def _redis() -> Redis:
    return Redis.from_url(REDIS_URL, decode_responses=True)


def _resume_score(resume_text: str, job: Job) -> int:
    tokens = set((resume_text + " " + job.role).lower().replace(",", " ").split())
    jd_tokens = set(job.description.lower().replace(",", " ").split())
    if not jd_tokens:
        return 0
    overlap = len(tokens.intersection(jd_tokens))
    return int((overlap / len(jd_tokens)) * 100)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME}


@app.post("/api/resume/generate", response_model=ResumeResponse)
def generate_resume(payload: ResumeRequest) -> ResumeResponse:
    resume_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    keywords_line = ", ".join(payload.keywords) if payload.keywords else "N/A"

    content = (
        f"# {payload.profile.full_name}\n"
        f"Email: {payload.profile.email}\n"
        f"Target Role: {payload.target_role} @ {payload.target_company}\n\n"
        f"## Professional Summary\n{payload.profile.summary}\n\n"
        f"## Core Skills\n- "
        + "\n- ".join(payload.profile.skills)
        + "\n\n## Experience Highlights\n- "
        + "\n- ".join(payload.profile.experience)
        + f"\n\n## Job Targeting Keywords\n{keywords_line}\n"
    )

    return ResumeResponse(resume_id=resume_id, generated_at=now, content=content)


@app.post("/api/jobs/auto-apply", response_model=QueueResult)
def auto_apply(payload: AutoApplyRequest) -> QueueResult:
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="jobs cannot be empty")

    redis = _redis()
    queued = 0

    for job in payload.jobs:
        score = _resume_score(payload.resume_text, job)
        if score < 10:
            continue

        application = {
            "application_id": str(uuid.uuid4()),
            "resume_id": payload.resume_id,
            "score": score,
            "auto_submit": payload.auto_submit,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "job": job.model_dump(),
        }
        redis.rpush(QUEUE_KEY, json.dumps(application))
        queued += 1

    return QueueResult(queued=queued, queue_key=QUEUE_KEY)


@app.get("/api/jobs/queue-size")
def queue_size() -> dict[str, int]:
    redis = _redis()
    return {"size": redis.llen(QUEUE_KEY)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
