from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.database import get_db
from app.models.user import User
from pydantic import BaseModel, EmailStr
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    department: str
    role: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpassword123",
                "full_name": "John Doe",
                "department": "IT",
                "role": "user"
            }
        }

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    async with db as session:
        # Check for both username and email
        result = await session.execute(
            select(User).where(
                (User.username == form_data.username) | (User.email == form_data.username)
            )
        )
        user = result.scalar_one_or_none()
        
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
async def register(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    try:
        async with db as session:
            # Check if user exists
            result = await session.execute(
                select(User).where(
                    (User.username == user_in.username) | (User.email == user_in.email)
                )
            )
            existing_user = result.scalar_one_or_none()
            if existing_user:
                if existing_user.email == user_in.email:
                    raise HTTPException(
                        status_code=400,
                        detail="Email already registered"
                    )
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Username already taken"
                    )
            
            # Validate role
            valid_roles = ["user", "admin", "analyst"]
            if user_in.role not in valid_roles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
                )

            # Create new user
            hashed_password = get_password_hash(user_in.password)
            user = User(
                email=user_in.email,
                username=user_in.username,
                hashed_password=hashed_password,
                full_name=user_in.full_name,
                department=user_in.department,
                role=user_in.role,
                is_active=True,
                is_superuser=False
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                subject=user.username, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        logger.error(f"Registration failed: {str(e.detail)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during registration"
        ) 