from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from optimizer.optimizer import PipelineOptimizer

app = FastAPI(title="Intelligent CI/CD Pipeline Optimizer")

# Request/response models

class Run(BaseModel):
    duration: float
    status: str
    job: str

class OptimizationReport(BaseModel):
    parallelization: List[str]
    caching: List[str]
    savings: str


# Routes

@app.get("/")
def root():
    return {"message": "CI/CD Optimizer API is running"}

@app.post("/optimize", response_model=OptimizationReport)
def optimize_pipeline(runs: List[Run]):
    """
    Accepts a list of CI/CD run results and returns optimization suggestions.
    """
    runs_dict = [dict(r) for r in runs]
    optimizer = PipelineOptimizer(runs_dict)
    report = optimizer.generate_report()
    return report
