from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.db import SessionLocal
from models.users import User
from src.schemas.user import UserCreate, User as UserSchema

router = APIRouter(prefix="/users", tags=["users"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(email=user.email, name=user.name)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("/{user_id}", response_model=UserSchema | None)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()
