from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.models.schemas import User, UserUpdate
from supabase import Client
from typing import List

router = APIRouter()

@router.get("/me", response_model=User)
async def get_current_user(
    db: Client = Depends(get_db)
) -> User:
    try:
        response = await db.auth.get_user()
        if response.error:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

@router.put("/me", response_model=User)
async def update_user(
    user_update: UserUpdate,
    db: Client = Depends(get_db)
) -> User:
    try:
        user = await get_current_user(db)
        response = await db.from_("profiles").update(user_update.model_dump(exclude_unset=True)).eq("id", user.id).execute()
        if response.error:
            raise HTTPException(
                status_code=400,
                detail=response.error.message
            )
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/", response_model=List[User])
async def get_users(
    db: Client = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    try:
        # Only superusers can list all users
        current_user = await get_current_user(db)
        if not current_user.user_metadata.get("role") == "admin":
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
            
        response = await db.from_("profiles").select("*").range(skip, skip + limit).execute()
        if response.error:
            raise HTTPException(
                status_code=400,
                detail=response.error.message
            )
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) 