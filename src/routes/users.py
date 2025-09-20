from fastapi import APIRouter, Depends
from src.core.db import db
from src.schemas.user import User
from src.middleware.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User)
async def create_user(user: User):
    # create user
    user_dict = user.dict(exclude={"id"})
    result = await db["users"].insert_one(user_dict)
    user.id = str(result.inserted_id)
    return user

@router.get("/{email}", response_model=User | None)
async def get_user(email: str):
    # get user
    user = await db["users"].find_one({"email": email})
    if user:
        return User(id=str(user["_id"]), email=user["email"], name=user["name"])
    return None

@router.get("/me/profile", response_model=dict)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    인증된 사용자의 프로필 정보를 반환하는 보호된 엔드포인트
    """
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "name": current_user["name"],
        "picture": current_user["picture"],
        "message": "Successfully authenticated with Firebase!"
    }

@router.put("/me/profile")
async def update_my_profile(
    user_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    인증된 사용자의 프로필을 업데이트하는 보호된 엔드포인트
    """
    # 현재 사용자의 UID를 기반으로 프로필 업데이트 로직
    return {
        "message": "Profile updated successfully",
        "uid": current_user["uid"],
        "updated_data": user_data
    }
