from fastapi import FastAPI
from src.routes import users, write, auth
from fastapi.middleware.cors import CORSMiddleware
from src.core.writing_review.writing_review import get_writing_review
#from src.models.user import Base
#from src.core.db import engine

app = FastAPI()
app.include_router(auth.auth)
app.include_router(users.users)
app.include_router(write.write)

origins = [
    "http://localhost:8080",
    "http://localhost:8081",
    "https://ielts-frontend-tau.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup():
#     # Create tables
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"message": "IELTS Backend API running with PostgreSQL!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
