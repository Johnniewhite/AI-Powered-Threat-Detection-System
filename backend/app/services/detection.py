from fastapi import UploadFile
import torch
from transformers import ViTImageProcessor, ViTForImageClassification
from transformers import pipeline
from PIL import Image
import io
import numpy as np
from app.core.config import settings

# Initialize models
text_classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    tokenizer="unitary/toxic-bert"
)

image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
image_model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")

async def analyze_image(file: UploadFile) -> dict:
    """Analyze image for potential insider threats"""
    # Read and preprocess image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Process image
    inputs = image_processor(images=image, return_tensors="pt")
    outputs = image_model(**inputs)
    probs = outputs.logits.softmax(1)
    
    # Calculate threat score (example implementation)
    threat_score = float(probs.max().item())
    confidence_score = float(probs.std().item())
    
    return {
        "threat_score": threat_score,
        "confidence_score": confidence_score,
        "category": "suspicious_image" if threat_score > settings.CONFIDENCE_THRESHOLD else "normal",
        "details": {
            "probabilities": probs.tolist(),
            "analysis_type": "image",
            "suspicious_elements": ["element1", "element2"] if threat_score > settings.CONFIDENCE_THRESHOLD else []
        },
        "remediation": {
            "actions": ["review_content", "flag_for_investigation"] if threat_score > settings.CONFIDENCE_THRESHOLD else [],
            "priority": "high" if threat_score > 0.8 else "medium" if threat_score > 0.5 else "low"
        }
    }

async def analyze_text(text: str) -> dict:
    """Analyze text for potential insider threats"""
    # Process text
    result = text_classifier(text)
    
    # Calculate threat score (example implementation)
    threat_score = float(max(result[0]['score'], 0.1))
    confidence_score = float(np.mean([r['score'] for r in result]))
    
    return {
        "threat_score": threat_score,
        "confidence_score": confidence_score,
        "category": "suspicious_text" if threat_score > settings.CONFIDENCE_THRESHOLD else "normal",
        "details": {
            "sentiment": result[0]['label'],
            "analysis_type": "text",
            "suspicious_phrases": ["phrase1", "phrase2"] if threat_score > settings.CONFIDENCE_THRESHOLD else []
        },
        "remediation": {
            "actions": ["review_content", "flag_for_investigation"] if threat_score > settings.CONFIDENCE_THRESHOLD else [],
            "priority": "high" if threat_score > 0.8 else "medium" if threat_score > 0.5 else "low"
        }
    }

async def analyze_multimodal(file: UploadFile, text: str) -> dict:
    """Analyze both image and text for potential insider threats"""
    # Get individual analyses
    image_result = await analyze_image(file)
    text_result = await analyze_text(text)
    
    # Combine scores (example implementation)
    threat_score = max(image_result["threat_score"], text_result["threat_score"])
    confidence_score = np.mean([image_result["confidence_score"], text_result["confidence_score"]])
    
    return {
        "threat_score": float(threat_score),
        "confidence_score": float(confidence_score),
        "category": "suspicious_multimodal" if threat_score > settings.CONFIDENCE_THRESHOLD else "normal",
        "details": {
            "image_analysis": image_result["details"],
            "text_analysis": text_result["details"],
            "analysis_type": "multimodal"
        },
        "remediation": {
            "actions": ["review_content", "flag_for_investigation"] if threat_score > settings.CONFIDENCE_THRESHOLD else [],
            "priority": "high" if threat_score > 0.8 else "medium" if threat_score > 0.5 else "low"
        }
    } 