from fastapi import APIRouter, Depends
from src.schemas.user import User
from src.middleware.auth import get_current_user

users = APIRouter(prefix="/users", tags=["users"])

@users.get("/me/profile", response_model=dict)
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
