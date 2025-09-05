from fastapi import FastAPI
from app.routes import users

app = FastAPI(title = "ielts API")

app.include_router(users.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


