from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.database import get_db
from app.schemas.dashboard import DashboardStats
from supabase import Client

router = APIRouter()
security = HTTPBearer()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db)
):
    try:
        # Get user from token
        token = credentials.credentials
        try:
            user = db.auth.get_user(token)
            if not user or not user.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            user_id = user.user.id
        except Exception as auth_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(auth_error)}"
            )

        # Get total detections for the user
        total_result = db.table("detections").select("*", count="exact").eq("user_id", user_id).execute()
        total_detections = len(total_result.data) if total_result.data else 0

        # Get high risk detections
        high_risk_result = db.table("detections").select("*").eq("user_id", user_id).gte("threat_score", 0.7).execute()
        high_risk = len(high_risk_result.data) if high_risk_result.data else 0

        # Get medium risk detections
        medium_risk_result = db.table("detections").select("*").eq("user_id", user_id).gte("threat_score", 0.4).lt("threat_score", 0.7).execute()
        medium_risk = len(medium_risk_result.data) if medium_risk_result.data else 0

        # Get low risk detections
        low_risk_result = db.table("detections").select("*").eq("user_id", user_id).lt("threat_score", 0.4).execute()
        low_risk = len(low_risk_result.data) if low_risk_result.data else 0

        # Get recent detections
        recent_result = db.table("detections").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(5).execute()
        recent_detections = recent_result.data if recent_result.data else []

        return {
            "total_detections": total_detections,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "recent_detections": recent_detections
        }
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
        ) 