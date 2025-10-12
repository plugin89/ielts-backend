from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.middleware.auth import get_current_user
from src.core.db import supabase
from datetime import datetime

auth = APIRouter(prefix="/auth", tags=["auth"])

class UserSyncRequest(BaseModel):
    uid: str
    email: str
    name: str | None = None
    picture: str | None = None

class UserSyncResponse(BaseModel):
    success: bool
    message: str
    user: dict | None = None
    is_new_user: bool

@auth.post("/sync", response_model=UserSyncResponse)
async def sync_user(current_user: dict = Depends(get_current_user)):
    """
    로그인 시 Supabase user 테이블에 유저 정보를 동기화하는 엔드포인트
    첫 로그인(회원가입)인 경우 새로운 레코드를 생성하고,
    기존 유저인 경우 정보를 업데이트합니다.
    """
    try:
        uid = current_user.get("uid")
        email = current_user.get("email")
        name = current_user.get("name")
        picture = current_user.get("picture")

        if not uid or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required user information (uid or email)"
            )

        # Check if user exists
        response = supabase.table("users").select("*").eq("uid", uid).execute()

        is_new_user = len(response.data) == 0

        if is_new_user:
            # Create new user
            user_data = {
                "uid": uid,
                "email": email,
                "name": name,
                "picture": picture,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            insert_response = supabase.table("users").insert(user_data).execute()

            return UserSyncResponse(
                success=True,
                message="New user created successfully",
                user=insert_response.data[0] if insert_response.data else None,
                is_new_user=True
            )
        else:
            # Update existing user
            update_data = {
                "email": email,
                "name": name,
                "picture": picture,
                "updated_at": datetime.utcnow().isoformat()
            }
            update_response = supabase.table("users").update(update_data).eq("uid", uid).execute()

            return UserSyncResponse(
                success=True,
                message="User information updated successfully",
                user=update_response.data[0] if update_response.data else None,
                is_new_user=False
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync user: {str(e)}"
        )
