from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.db import get_db
from ..models import Repository, PipelineRun, JobRun
from ..schemas.events import IngestEvent, RunStarted, RunCompleted, JobStarted, JobCompleted

router = APIRouter(prefix="/events", tags=["events"])

def get_or_create_repo(db: Session, provider: str, name: str) -> Repository:
    repo = db.query(Repository).filter_by(provider=provider, name=name).one_or_none()
    if repo is None:
        repo = Repository(provider=provider, name=name)
        db.add(repo)
        db.flush()
    return repo

def get_or_create_run(db: Session, repo_id: int, provider_run_id: str) -> PipelineRun:
    run = db.query(PipelineRun).filter_by(repo_id=repo_id, provider_run_id=provider_run_id).one_or_none()
    if run is None:
        run = PipelineRun(repo_id=repo_id, provider_run_id=provider_run_id)
        db.add(run)
        db.flush()
    return run

@router.post("/ingest")
def ingest(event: IngestEvent, db: Session = Depends(get_db)):
    # Upsert repo + run baseline
    repo = get_or_create_repo(db, event.repo.provider, event.repo.name)
    run = get_or_create_run(db, repo.id, event.run.provider_run_id)

    # Apply per-event updates
    if isinstance(event, RunStarted):
        run.started_at = event.started_at
        run.queue_duration_sec = event.queue_duration_sec
        run.commit_sha = event.run.commit_sha
        run.branch = event.run.branch
        run.status = "running"
    elif isinstance(event, RunCompleted):
        run.started_at = event.started_at
        run.completed_at = event.completed_at
        run.total_duration_sec = event.total_duration_sec
        run.status = event.status
    elif isinstance(event, JobStarted):
        job = JobRun(
            pipeline_run_id=run.id,
            job_name=event.job_name,
            status="running",
            runner_label=event.runner_label,
            attempt=event.attempt,
            started_at=event.started_at,
        )
        db.add(job)
    elif isinstance(event, JobCompleted):
        job = db.query(JobRun).filter_by(
            pipeline_run_id=run.id, job_name=event.job_name
        ).order_by(JobRun.id.desc()).first()
        if not job:
            # tolerate out-of-order: create if missing
            job = JobRun(pipeline_run_id=run.id, job_name=event.job_name, started_at=event.started_at)
            db.add(job)
            db.flush()
        job.completed_at = event.completed_at
        job.status = event.status
        job.duration_sec = event.duration_sec
        job.queued_sec = event.queued_sec
        job.cache_hit = event.cache_hit
        job.cpu_min = event.cpu_min
        job.mem_mb = event.mem_mb
        job.artifacts_mb = event.artifacts_mb
    else:
        raise HTTPException(status_code=400, detail="Unsupported event")

    db.commit()
    return {"ok": True, "repo_id": repo.id, "run_id": run.id}
