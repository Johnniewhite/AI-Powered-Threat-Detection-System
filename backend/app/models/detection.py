from sqlalchemy import String, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from typing import Optional, Dict, List

class ThreatDetection(BaseModel):
    __tablename__ = "threat_detections"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    detection_type: Mapped[str] = mapped_column(String)  # 'image', 'text', or 'multimodal'
    content_path: Mapped[str] = mapped_column(String)  # Path to the analyzed content
    threat_score: Mapped[float] = mapped_column(Float)
    confidence_score: Mapped[float] = mapped_column(Float)
    analysis_results: Mapped[Dict] = mapped_column(JSON)  # Detailed analysis results
    threat_category: Mapped[str] = mapped_column(String)  # Type of threat detected
    remediation_suggestions: Mapped[Dict] = mapped_column(JSON)  # Suggested actions
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="detections") 