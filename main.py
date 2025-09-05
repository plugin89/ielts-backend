from fastapi import FastAPI
from src.routes import users
from src.models.user import Base
from src.core.db import engine

app = FastAPI()
app.include_router(users.router)

@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"message": "IELTS Backend API running with PostgreSQL!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

