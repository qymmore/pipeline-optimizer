from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

# Generic event types we accept (kept simple for MVP)
EventType = Literal["run_started", "run_completed", "job_started", "job_completed"]

class RepoRef(BaseModel):
    provider: Literal["github", "jenkins", "gitlab"] = "github"
    name: str                                # "org/repo" or job name

class RunRef(BaseModel):
    provider_run_id: str
    commit_sha: Optional[str] = None
    branch: Optional[str] = None

class BaseEvent(BaseModel):
    repo: RepoRef
    run: RunRef
    event_type: EventType

class RunStarted(BaseEvent):
    started_at: datetime
    queue_duration_sec: float | None = None

class RunCompleted(BaseEvent):
    started_at: datetime
    completed_at: datetime
    status: Literal["success","failed","canceled"]
    total_duration_sec: float

class JobStarted(BaseEvent):
    job_name: str
    started_at: datetime
    runner_label: str | None = None
    attempt: int = 1

class JobCompleted(BaseEvent):
    job_name: str
    started_at: datetime
    completed_at: datetime
    status: Literal["success","failed","skipped","canceled"]
    duration_sec: float
    queued_sec: float | None = None
    cache_hit: bool = False
    cpu_min: float | None = None
    mem_mb: float | None = None
    artifacts_mb: float | None = None

IngestEvent = RunStarted | RunCompleted | JobStarted | JobCompleted
