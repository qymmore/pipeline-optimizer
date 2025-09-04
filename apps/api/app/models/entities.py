from sqlalchemy import String, Integer, BigInteger, ForeignKey, DateTime, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ..core.db import Base

class Repository(Base):
    __tablename__ = "repositories"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(32), index=True)  # "github" | "jenkins" | "gitlab"
    name: Mapped[str] = mapped_column(String(255), index=True)     # "org/repo" or job path
    default_branch: Mapped[str] = mapped_column(String(120), default="main")
    runs: Mapped[list["PipelineRun"]] = relationship(back_populates="repo", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("provider", "name", name="uq_repo_provider_name"),)

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), index=True)
    provider_run_id: Mapped[str] = mapped_column(String(128), index=True)  # e.g., GHA run_id or Jenkins build number
    commit_sha: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    branch: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="queued")      # queued|running|success|failed|canceled
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    queue_duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)

    repo: Mapped["Repository"] = relationship(back_populates="runs")
    jobs: Mapped[list["JobRun"]] = relationship(back_populates="pipeline", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("repo_id", "provider_run_id", name="uq_repo_run"),)

class JobRun(Base):
    __tablename__ = "job_runs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pipeline_run_id: Mapped[int] = mapped_column(ForeignKey("pipeline_runs.id", ondelete="CASCADE"), index=True)
    job_name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(24), default="running")     # running|success|failed|skipped|canceled
    runner_label: Mapped[str | None] = mapped_column(String(120), nullable=True)  # e.g., "ubuntu-latest"
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    queued_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    cpu_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    mem_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    artifacts_mb: Mapped[float | None] = mapped_column(Float, nullable=True)

    pipeline: Mapped["PipelineRun"] = relationship(back_populates="jobs")
