from fastapi import FastAPI
from src.routes import users, write
from fastapi.middleware.cors import CORSMiddleware
from src.core.writing_review.writing_review import get_writing_review
from src.core.firebase import initialize_firebase
from contextlib import asynccontextmanager
#from src.models.user import Base
#from src.core.db import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)
app.include_router(users.users)
app.include_router(write.write)

origins = [
    "http://localhost:8080",
    "https://ielts-frontend-tau.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "IELTS Backend API running with PostgreSQL!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
