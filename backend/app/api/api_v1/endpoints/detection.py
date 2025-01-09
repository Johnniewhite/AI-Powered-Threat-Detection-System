from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.core.database import get_db
from app.models.schemas import Detection, DetectionCreate, DetectionUpdate
from supabase import Client
from pydantic import BaseModel
from datetime import datetime

class TextAnalysisRequest(BaseModel):
    text: str

def format_datetime(dt: datetime) -> str:
    return dt.isoformat() if dt else None

router = APIRouter()

@router.post("/", response_model=Detection)
async def create_detection(
    detection: DetectionCreate,
    db: Client = Depends(get_db)
):
    try:
        result = await db.table("detections").insert(detection.model_dump()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Detection])
async def get_detections(
    skip: int = 0,
    limit: int = 100,
    db: Client = Depends(get_db)
):
    try:
        # Get current user
        user_response = await db.auth.get_user()
        if user_response.error:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = user_response.data
        
        result = await db.from_("detections")\
            .select("*")\
            .eq("user_id", user.id)\
            .range(skip, skip + limit)\
            .order("created_at", desc=True)\
            .execute()
            
        return result.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze/image", response_model=Detection)
async def analyze_image(
    file: UploadFile = File(...),
    db: Client = Depends(get_db)
):
    try:
        # Get current user
        user_response = db.auth.get_user()
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = user_response.user

        try:
            # Check if user profile exists
            profile = db.table("profiles").select("*").eq("id", user.id).execute()
            
            if not profile.data:
                # Create user profile with minimal required fields
                profile_data = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.email.split('@')[0] if user.email else f"user_{user.id}",
                    "created_at": format_datetime(datetime.utcnow()),
                    "updated_at": format_datetime(datetime.utcnow())
                }
                profile_result = db.table("profiles").insert(profile_data).execute()
                if not profile_result.data:
                    raise HTTPException(status_code=500, detail="Failed to create user profile")
        except Exception as profile_error:
            print(f"Profile error: {str(profile_error)}")
            raise HTTPException(status_code=500, detail="Error managing user profile")
        
        # Process image
        try:
            content = await file.read()
            
            # Generate a unique file path for the image
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
            storage_path = f"{user.id}/{safe_filename}"
            
            # Upload file to Supabase Storage
            try:
                storage_response = db.storage.from_("threat-images").upload(
                    path=storage_path,
                    file=content,
                    file_options={"content-type": file.content_type}
                )
                
                # Get the public URL
                file_url = db.storage.from_("threat-images").get_public_url(storage_path)
                
            except Exception as upload_error:
                print(f"Storage error: {str(upload_error)}")
                raise HTTPException(status_code=500, detail="Failed to upload image")
            
            # Create detection record
            detection_data = {
                "user_id": user.id,
                "detection_type": "image",
                "content_path": file_url,  # Store the public URL
                "threat_score": 0.7,  # Example score
                "confidence_score": 0.85,  # Example score
                "analysis_results": {
                    "details": f"Analysis of image: {file.filename}",
                    "indicators": ["suspicious pattern", "known malicious signature"]
                },
                "threat_category": "malware",
                "remediation_suggestions": {
                    "actions": [
                        "Quarantine file",
                        "Scan system for similar patterns",
                        "Update security definitions"
                    ],
                    "priority": "high"
                },
                "created_at": format_datetime(datetime.utcnow()),
                "updated_at": format_datetime(datetime.utcnow())
            }
            
            result = db.table("detections").insert(detection_data).execute()
            if not result.data:
                # If detection creation fails, try to delete the uploaded file
                try:
                    db.storage.from_("threat-images").remove([storage_path])
                except:
                    pass
                raise HTTPException(status_code=500, detail="Failed to create detection")
            
            return result.data[0]
            
        except Exception as detection_error:
            print(f"Detection error: {str(detection_error)}")
            raise HTTPException(status_code=500, detail="Error creating detection record")

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/analyze/text", response_model=Detection)
async def analyze_text(
    request: TextAnalysisRequest,
    db: Client = Depends(get_db)
):
    try:
        # Get current user
        user_response = db.auth.get_user()
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = user_response.user

        try:
            # Check if user profile exists
            profile = db.table("profiles").select("*").eq("id", user.id).execute()
            
            if not profile.data:
                # Create user profile with minimal required fields
                profile_data = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.email.split('@')[0] if user.email else f"user_{user.id}",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                try:
                    profile_result = db.table("profiles").insert(profile_data).execute()
                    if not profile_result.data:
                        print("Failed to create profile, no data returned")
                        raise HTTPException(status_code=500, detail="Failed to create user profile")
                except Exception as insert_error:
                    print(f"Profile insertion error: {str(insert_error)}")
                    raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(insert_error)}")
        except Exception as profile_error:
            print(f"Profile error: {str(profile_error)}")
            raise HTTPException(status_code=500, detail=f"Error managing user profile: {str(profile_error)}")

        # Create detection with current timestamp
        current_time = datetime.utcnow().isoformat()
        detection_data = {
            "user_id": user.id,
            "detection_type": "text",
            "content_path": "",
            "threat_score": 0.6,
            "confidence_score": 0.9,
            "analysis_results": {
                "details": f"Analysis of text: {request.text[:100]}...",
                "indicators": ["suspicious links", "urgent language", "credential request"]
            },
            "threat_category": "phishing",
            "remediation_suggestions": {
                "actions": [
                    "Block sender",
                    "Report to security team",
                    "User awareness training"
                ],
                "priority": "medium"
            },
            "created_at": current_time,
            "updated_at": current_time
        }
        
        try:
            result = db.table("detections").insert(detection_data).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create detection")
            return result.data[0]
        except Exception as detection_error:
            print(f"Detection error: {str(detection_error)}")
            raise HTTPException(status_code=500, detail=f"Error creating detection record: {str(detection_error)}")

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Text analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 