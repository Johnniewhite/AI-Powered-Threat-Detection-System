from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    department: Optional[str] = None
    role: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None

class DetectionBase(BaseModel):
    detection_type: str
    content_path: str
    threat_score: float
    confidence_score: float
    analysis_results: Dict
    threat_category: str
    remediation_suggestions: Dict

class DetectionCreate(DetectionBase):
    user_id: str

class DetectionUpdate(BaseModel):
    threat_score: Optional[float] = None
    confidence_score: Optional[float] = None
    analysis_results: Optional[Dict] = None
    remediation_suggestions: Optional[Dict] = None

class Detection(DetectionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    detections: Optional[List[Detection]] = []

    class Config:
        from_attributes = True 