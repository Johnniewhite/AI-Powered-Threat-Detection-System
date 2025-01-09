from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import get_db
from typing import Dict
from supabase import Client

router = APIRouter()

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Client = Depends(get_db)
) -> Dict:
    try:
        auth_response = db.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "token_type": "bearer",
            "user": auth_response.user
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

@router.post("/logout")
async def logout(
    db: Client = Depends(get_db)
) -> Dict:
    try:
        # Get current session and sign out
        db.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return {"message": "Successfully logged out"}  # Always return success for logout

@router.post("/signup")
async def signup(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Client = Depends(get_db)
) -> Dict:
    try:
        auth_response = db.auth.sign_up({
            "email": form_data.username,
            "password": form_data.password,
            "options": {
                "data": {
                    "username": form_data.username.split('@')[0],
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
        return {
            "access_token": auth_response.session.access_token if auth_response.session else None,
            "refresh_token": auth_response.session.refresh_token if auth_response.session else None,
            "token_type": "bearer",
            "user": auth_response.user
        }
    except Exception as e:
        print(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Failed to create user"
        ) 