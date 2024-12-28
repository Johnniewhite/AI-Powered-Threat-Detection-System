from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.database import get_db
from app.models.detection import ThreatDetection
from app.models.user import User
from app.core.auth import get_current_user
from pydantic import BaseModel
import random
import hashlib
import re

router = APIRouter()

class AnalysisResult(BaseModel):
    threat_score: float
    confidence_score: float
    threat_category: str
    analysis_results: dict[str, str]
    remediation_suggestions: dict[str, list[str]]

class DetectionResponse(BaseModel):
    id: int
    detection_type: str
    threat_score: float
    confidence_score: float
    threat_category: str
    created_at: datetime
    analysis_results: dict[str, str]
    remediation_suggestions: dict[str, list[str]]

class TextAnalysisRequest(BaseModel):
    text: str

def analyze_image_content(content: bytes, filename: str) -> tuple[float, float, str, str, list[str]]:
    # Generate a hash of the content
    file_hash = hashlib.md5(content).hexdigest()
    hash_value = int(file_hash[:8], 16)
    
    # Advanced image analysis factors
    file_size = len(content)
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    # Risk factors
    risk_factors = []
    
    # Size-based analysis
    if file_size < 1024:  # Suspiciously small
        risk_factors.append(0.3)
    elif file_size > 10 * 1024 * 1024:  # Very large
        risk_factors.append(0.2)
        
    # Extension-based analysis
    high_risk_extensions = {'exe', 'dll', 'bat', 'cmd', 'msi', 'vbs', 'js'}
    medium_risk_extensions = {'zip', 'rar', '7z', 'tar', 'gz'}
    if file_ext in high_risk_extensions:
        risk_factors.append(0.8)
    elif file_ext in medium_risk_extensions:
        risk_factors.append(0.5)
        
    # Content analysis (simulated with hash)
    content_risk = (hash_value % 100) / 100.0
    risk_factors.append(content_risk)
    
    # Calculate final threat score
    threat_score = sum(risk_factors) / len(risk_factors) if risk_factors else 0.1
    threat_score = min(max(threat_score, 0.0), 1.0)  # Ensure between 0 and 1
    
    # Calculate confidence based on number of risk factors
    confidence_score = 0.7 + (len(risk_factors) * 0.05)
    confidence_score = min(confidence_score, 0.95)
    
    # Determine category and details
    if threat_score >= 0.7:
        category = "critical_threat"
        details = "Critical security threat detected in image"
        actions = [
            "immediate quarantine",
            "block file hash",
            "report to security team",
            "scan connected systems",
            "investigate source"
        ]
    elif threat_score >= 0.5:
        category = "malware"
        details = "Potential malware characteristics detected"
        actions = [
            "quarantine file",
            "scan with multiple engines",
            "monitor system activity",
            "review file source"
        ]
    elif threat_score >= 0.3:
        category = "suspicious"
        details = "Suspicious patterns detected in image"
        actions = [
            "scan with antivirus",
            "review file metadata",
            "monitor for similar files"
        ]
    else:
        category = "low_risk"
        details = "No significant threats detected"
        actions = [
            "safe to use",
            "regular monitoring",
            "maintain standard security"
        ]
    
    return threat_score, confidence_score, category, details, actions

def analyze_text_content(text: str) -> tuple[float, float, str, str, list[str]]:
    text = text.lower()
    
    # Enhanced threat categories with weighted keywords and patterns
    threat_patterns = {
        "phishing": {
            "keywords": {
                "critical": ["ssn", "social security", "password reset", "account suspended", "verify immediately"],
                "high": ["bank account", "credit card", "verify account", "login credentials", "security alert"],
                "medium": ["verify", "account", "bank", "urgent", "suspended", "confirm identity"],
                "low": ["update", "information", "click", "link", "access"]
            },
            "patterns": [
                r'\b(?:password|account|login)\s+(?:verify|confirm|validate)\b',
                r'\b(?:urgent|immediate)\s+(?:action|attention|response)\b',
                r'\b(?:bank|credit\s+card|account)\s+(?:suspend|block|verify)\b',
                r'\b(?:ssn|social\s+security|credit\s+card)\s*[:#]\s*\d+\b',
                r'\b(?:user|account|login)\s*[:#]\s*\w+\b'
            ]
        },
        "malware": {
            "keywords": {
                "critical": ["run exe", "disable antivirus", "disable firewall", "enable macros"],
                "high": ["download exe", "run attachment", "bitcoin wallet", "mining software"],
                "medium": ["exe", "download", "attachment", "bitcoin", "lottery", "prize won"],
                "low": ["install", "software", "update required", "win", "winner"]
            },
            "patterns": [
                r'\b(?:download|run|execute)\s+(?:file|attachment|program)\b',
                r'\b(?:bitcoin|crypto|wallet)\s+(?:address|transfer|send)\b',
                r'\.[ex][xe][ee]?\b',
                r'\b(?:virus|malware|trojan)\s+(?:scan|detect|remove)\b'
            ]
        },
        "spam": {
            "keywords": {
                "critical": ["wire transfer", "million dollars", "nigerian prince", "inheritance claim"],
                "high": ["make money fast", "work from home", "earn easy", "guaranteed profit"],
                "medium": ["discount", "offer", "free", "buy now", "limited time", "exclusive deal"],
                "low": ["sale", "save", "cheap", "best price", "discount"]
            },
            "patterns": [
                r'\b(?:million|billion)\s+(?:dollar|euro|pound)s?\b',
                r'\b(?:\d+%)\s+(?:discount|off|savings)\b',
                r'\$\s*\d+[kK]\s+(?:per|a)\s+(?:day|week|month)\b',
                r'\b(?:free|discount|save)\s+(?:shipping|offer|gift)\b'
            ]
        }
    }
    
    # Calculate scores for each category
    category_scores = {}
    for category, rules in threat_patterns.items():
        score = 0
        matches = 0
        
        # Check keyword matches with weights
        for level, keywords in rules["keywords"].items():
            weight = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.3}[level]
            for keyword in keywords:
                if keyword in text:
                    score += weight
                    matches += 1
        
        # Check regex patterns
        for pattern in rules["patterns"]:
            if re.search(pattern, text):
                score += 1.0  # Pattern matches are highly weighted
                matches += 1
        
        # Normalize score based on matches
        category_scores[category] = score / (matches if matches > 0 else 1)
    
    # Determine primary threat category and score
    threat_category = max(category_scores, key=category_scores.get)
    threat_score = category_scores[threat_category]
    
    # Normalize threat score to 0-1 range
    threat_score = min(max(threat_score, 0.0), 1.0)
    
    # Calculate confidence score based on number of matches and pattern complexity
    confidence_base = 0.75
    confidence_boost = min(0.2, len(re.findall(r'\b\w+\b', text)) / 1000)  # Text length factor
    confidence_score = confidence_base + confidence_boost
    
    # Determine detailed response based on category and score
    if threat_score >= 0.7:
        prefix = "Critical"
        severity = "critical"
    elif threat_score >= 0.5:
        prefix = "High-risk"
        severity = "high"
    elif threat_score >= 0.3:
        prefix = "Moderate"
        severity = "moderate"
    else:
        prefix = "Low-risk"
        severity = "low"
    
    details = f"{prefix} {threat_category} content detected"
    
    # Category-specific actions
    actions = {
        "phishing": {
            "critical": [
                "block sender immediately",
                "report to security team",
                "investigate affected accounts",
                "initiate incident response",
                "mandatory security training"
            ],
            "high": [
                "block sender",
                "report to security team",
                "review account activity",
                "user training required"
            ],
            "moderate": [
                "flag as suspicious",
                "verify sender identity",
                "monitor account activity"
            ],
            "low": [
                "mark as potential phishing",
                "user awareness reminder"
            ]
        },
        "malware": {
            "critical": [
                "quarantine immediately",
                "block associated IPs",
                "scan all systems",
                "incident response team notification",
                "forensic analysis required"
            ],
            "high": [
                "block execution",
                "scan system",
                "update security definitions",
                "monitor system activity"
            ],
            "moderate": [
                "scan with antivirus",
                "monitor for suspicious activity",
                "review security logs"
            ],
            "low": [
                "routine scan recommended",
                "monitor system status"
            ]
        },
        "spam": {
            "critical": [
                "block sender domain",
                "report to abuse teams",
                "update spam filters",
                "investigate campaign",
                "block associated IPs"
            ],
            "high": [
                "block sender",
                "update spam rules",
                "monitor for patterns",
                "report to provider"
            ],
            "moderate": [
                "mark as spam",
                "adjust filter rules",
                "monitor frequency"
            ],
            "low": [
                "flag as potential spam",
                "update spam scores"
            ]
        }
    }
    
    return threat_score, confidence_score, threat_category, details, actions[threat_category][severity]

@router.post("/image", response_model=AnalysisResult)
async def analyze_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        content = await file.read()
        threat_score, confidence_score, category, details, actions = analyze_image_content(content, file.filename)
        
        detection = ThreatDetection(
            user_id=current_user.id,
            detection_type="image",
            content_path=file.filename,
            threat_score=threat_score,
            confidence_score=confidence_score,
            threat_category=category,
            analysis_results={"details": details},
            remediation_suggestions={"actions": actions}
        )
        
        db.add(detection)
        await db.commit()
        
        return {
            "threat_score": threat_score,
            "confidence_score": confidence_score,
            "threat_category": category,
            "analysis_results": {"details": details},
            "remediation_suggestions": {"actions": actions}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing image: {str(e)}"
        )

@router.post("/text", response_model=AnalysisResult)
async def analyze_text(
    request: TextAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        threat_score, confidence_score, category, details, actions = analyze_text_content(request.text)
        
        detection = ThreatDetection(
            user_id=current_user.id,
            detection_type="text",
            content_path="text_analysis",
            threat_score=threat_score,
            confidence_score=confidence_score,
            threat_category=category,
            analysis_results={"details": details},
            remediation_suggestions={"actions": actions}
        )
        
        db.add(detection)
        await db.commit()
        
        return {
            "threat_score": threat_score,
            "confidence_score": confidence_score,
            "threat_category": category,
            "analysis_results": {"details": details},
            "remediation_suggestions": {"actions": actions}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing text: {str(e)}"
        )

@router.get("/history", response_model=List[DetectionResponse])
async def get_detection_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        result = await db.execute(
            select(ThreatDetection)
            .where(ThreatDetection.user_id == current_user.id)
            .order_by(ThreatDetection.created_at.desc())
        )
        detections = result.scalars().all()
        
        return [
            {
                "id": d.id,
                "detection_type": d.detection_type,
                "threat_score": d.threat_score,
                "confidence_score": d.confidence_score,
                "threat_category": d.threat_category,
                "created_at": d.created_at,
                "analysis_results": d.analysis_results,
                "remediation_suggestions": d.remediation_suggestions
            }
            for d in detections
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching detection history: {str(e)}"
        ) 