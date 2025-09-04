from fastapi import FastAPI
from .core.db import Base, engine
from .routers import health, events

app = FastAPI(title="Intelligent CI/CD Pipeline Optimizer API")

# Create tables on startup (swap to Alembic later)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(health.router)
app.include_router(events.router)
