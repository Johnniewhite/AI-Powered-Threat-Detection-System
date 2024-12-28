from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.deps import get_current_active_user, get_current_active_superuser
from app.core.database import get_db
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class UserBase(BaseModel):
    email: str
    username: str
    full_name: str | None = None
    department: str | None = None
    role: str | None = None
    is_active: bool = True
    is_superuser: bool = False

class UserUpdate(UserBase):
    password: str | None = None

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserOut)
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return current_user

@router.put("/me", response_model=UserOut)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    async with db as session:
        if user_in.password is not None:
            from app.core.security import get_password_hash
            current_user.hashed_password = get_password_hash(user_in.password)
        if user_in.email is not None:
            current_user.email = user_in.email
        if user_in.username is not None:
            current_user.username = user_in.username
        if user_in.full_name is not None:
            current_user.full_name = user_in.full_name
        if user_in.department is not None:
            current_user.department = user_in.department
        if user_in.role is not None:
            current_user.role = user_in.role
            
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
        return current_user

@router.get("/", response_model=List[UserOut])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    async with db as session:
        result = await session.execute(
            select(User).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return users

@router.get("/{user_id}", response_model=UserOut)
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db),
) -> Any:
    async with db as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        return user 