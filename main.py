from fastapi import FastAPI
from src.routes import users
from fastapi.middleware.cors import CORSMiddleware
from schemas.write import WritingInput, AIReview
from src.core.writing_review.writing_review import get_writing_review
#from src.models.user import Base
#from src.core.db import engine

app = FastAPI()
app.include_router(users.users)

origins = [
    "http://localhost:8080"
    "https://essay-buddy-ielts.lovable.app"
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

@app.post("/review")
def review_essay(user_writing_input: WritingInput) -> AIReview:
    # Dummy implementation for essay review
    # In a real scenario, this would involve complex logic or ML models
    review_result = await get_writing_review(user_writing_input)  # Just a placeholder
    return review_result