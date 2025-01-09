from typing import List
from pydantic import BaseModel
from datetime import datetime

class DetectionSummary(BaseModel):
    id: str
    threat_score: float
    threat_category: str
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_detections: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    recent_detections: List[DetectionSummary]

    class Config:
        from_attributes = True 