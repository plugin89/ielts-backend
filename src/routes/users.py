from fastapi import APIRouter
#from src.core.db import db
from src.schemas.user import User

users = APIRouter(prefix="/users", tags=["users"])

@users.post("/", response_model=User)
async def create_user(user: User):
    # create user
    user_dict = user.dict(exclude={"id"})
    result = await db["users"].insert_one(user_dict)
    user.id = str(result.inserted_id)
    return user

@users.get("/{email}", response_model=User | None)
async def get_user(email: str):
    # get user
    user = await db["users"].find_one({"email": email})
    if user:
        return User(id=str(user["_id"]), email=user["email"], name=user["name"])
    return None
