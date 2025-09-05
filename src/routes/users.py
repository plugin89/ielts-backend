from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_users():
    return [{"id": 1, "name": "Alice"}]

@router.post("/")
def create_user(name: str):
    return {"id": 2, "name": name}