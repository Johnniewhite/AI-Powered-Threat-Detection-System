from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.detection import ThreatDetection
from app.services.detection import analyze_image, analyze_text, analyze_multimodal
from pydantic import BaseModel
import json

router = APIRouter()

class DetectionResponse(BaseModel):
    id: int
    detection_type: str
    threat_score: float
    confidence_score: float
    threat_category: str
    analysis_results: dict
    remediation_suggestions: dict

    class Config:
        from_attributes = True

@router.post("/image", response_model=DetectionResponse)
async def detect_image_threat(
    *,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    # Analyze image
    analysis_result = await analyze_image(file)
    
    # Create detection record
    detection = ThreatDetection(
        user_id=current_user.id,
        detection_type="image",
        content_path=file.filename,
        threat_score=analysis_result["threat_score"],
        confidence_score=analysis_result["confidence_score"],
        analysis_results=analysis_result["details"],
        threat_category=analysis_result["category"],
        remediation_suggestions=analysis_result["remediation"]
    )
    
    async with db as session:
        session.add(detection)
        await session.commit()
        await session.refresh(detection)
    
    return detection

@router.post("/text", response_model=DetectionResponse)
async def detect_text_threat(
    *,
    db: AsyncSession = Depends(get_db),
    text: str = Form(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    # Analyze text
    analysis_result = await analyze_text(text)
    
    # Create detection record
    detection = ThreatDetection(
        user_id=current_user.id,
        detection_type="text",
        content_path="text_analysis",
        threat_score=analysis_result["threat_score"],
        confidence_score=analysis_result["confidence_score"],
        analysis_results=analysis_result["details"],
        threat_category=analysis_result["category"],
        remediation_suggestions=analysis_result["remediation"]
    )
    
    async with db as session:
        session.add(detection)
        await session.commit()
        await session.refresh(detection)
    
    return detection

@router.post("/multimodal", response_model=DetectionResponse)
async def detect_multimodal_threat(
    *,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    text: str = Form(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    # Analyze both image and text
    analysis_result = await analyze_multimodal(file, text)
    
    # Create detection record
    detection = ThreatDetection(
        user_id=current_user.id,
        detection_type="multimodal",
        content_path=file.filename,
        threat_score=analysis_result["threat_score"],
        confidence_score=analysis_result["confidence_score"],
        analysis_results=analysis_result["details"],
        threat_category=analysis_result["category"],
        remediation_suggestions=analysis_result["remediation"]
    )
    
    async with db as session:
        session.add(detection)
        await session.commit()
        await session.refresh(detection)
    
    return detection

@router.get("/history", response_model=List[DetectionResponse])
async def get_detection_history(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    async with db as session:
        result = await session.execute(
            select(ThreatDetection)
            .where(ThreatDetection.user_id == current_user.id)
            .order_by(ThreatDetection.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        detections = result.scalars().all()
        return detections 