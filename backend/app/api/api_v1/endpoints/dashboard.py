from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, desc, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.detection import ThreatDetection
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        # Initialize seven_days_ago at the start
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # Get total detections
        total_result = await db.execute(
            select(func.count(ThreatDetection.id))
            .where(ThreatDetection.user_id == current_user.id)
        )
        total_detections = total_result.scalar() or 0

        # Get recent detections (last 24 hours)
        recent_result = await db.execute(
            select(func.count(ThreatDetection.id))
            .where(
                ThreatDetection.user_id == current_user.id,
                ThreatDetection.created_at >= datetime.utcnow() - timedelta(days=1)
            )
        )
        recent_detections = recent_result.scalar() or 0

        # Get severity counts using case()
        severity_result = await db.execute(
            select(
                case(
                    (ThreatDetection.threat_score >= 0.8, "critical"),
                    (ThreatDetection.threat_score >= 0.6, "high"),
                    (ThreatDetection.threat_score >= 0.4, "moderate"),
                    else_="low"
                ).label("severity"),
                func.count(ThreatDetection.id).label("count")
            )
            .where(ThreatDetection.user_id == current_user.id)
            .group_by("severity")
        )
        severity_counts = {
            "critical": 0,
            "high": 0,
            "moderate": 0,
            "low": 0
        }
        for severity, count in severity_result.all():
            severity_counts[severity] = count

        # Get threat categories
        category_result = await db.execute(
            select(
                ThreatDetection.threat_category,
                func.count(ThreatDetection.id)
            )
            .where(ThreatDetection.user_id == current_user.id)
            .group_by(ThreatDetection.threat_category)
        )
        threat_categories = {
            "phishing": 0,
            "malware": 0,
            "spam": 0,
            "suspicious": 0
        }
        for category, count in category_result.all():
            if category in threat_categories:
                threat_categories[category] = count

        # Get detection types
        types_result = await db.execute(
            select(
                ThreatDetection.detection_type,
                func.count(ThreatDetection.id)
            )
            .where(ThreatDetection.user_id == current_user.id)
            .group_by(ThreatDetection.detection_type)
        )
        detection_types = {
            "image": 0,
            "text": 0,
            "multimodal": 0,
            **(dict(types_result.all()) if types_result else {})
        }

        # Get detection trends (last 7 days)
        trends_result = await db.execute(
            select(
                func.date(ThreatDetection.created_at).label("date"),
                func.count(ThreatDetection.id).label("count")
            )
            .where(
                ThreatDetection.user_id == current_user.id,
                ThreatDetection.created_at >= seven_days_ago
            )
            .group_by("date")
            .order_by("date")
        )
        trends_data = dict(trends_result.all()) if trends_result else {}

        # Fill in missing dates
        trends = []
        for i in range(7):
            date = (seven_days_ago + timedelta(days=i)).date()
            trends.append({
                "date": date.isoformat(),
                "count": trends_data.get(date, 0)
            })

        return {
            "total_detections": total_detections,
            "recent_threats": severity_counts,
            "threat_categories": threat_categories,
            "detection_history": trends
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard stats: {str(e)}"
        )

@router.get("/recent")
async def get_recent_detections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        result = await db.execute(
            select(ThreatDetection)
            .where(ThreatDetection.user_id == current_user.id)
            .order_by(desc(ThreatDetection.created_at))
            .limit(10)
        )
        detections = result.scalars().all()

        return [
            {
                "id": detection.id,
                "detection_type": detection.detection_type,
                "threat_score": detection.threat_score,
                "confidence_score": detection.confidence_score,
                "threat_category": detection.threat_category,
                "created_at": detection.created_at,
                "analysis_results": detection.analysis_results,
                "remediation_suggestions": detection.remediation_suggestions
            }
            for detection in detections
        ]
    except Exception as e:
        print(f"Error in get_recent_detections: {str(e)}")
        return [] 