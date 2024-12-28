import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, async_session
from app.models.base import Base
from app.models.user import User
from app.models.detection import ThreatDetection
from app.core.security import get_password_hash
from datetime import datetime, timedelta

async def create_default_users(session: AsyncSession):
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="System Administrator",
        department="IT",
        role="admin",
        is_active=True,
        is_superuser=True
    )
    session.add(admin)

    # Create analyst user
    analyst = User(
        email="analyst@example.com",
        username="analyst",
        hashed_password=get_password_hash("analyst123"),
        full_name="Security Analyst",
        department="Security",
        role="analyst",
        is_active=True,
        is_superuser=False
    )
    session.add(analyst)

    # Create regular user
    user = User(
        email="user@example.com",
        username="user",
        hashed_password=get_password_hash("user123"),
        full_name="Regular User",
        department="Operations",
        role="user",
        is_active=True,
        is_superuser=False
    )
    session.add(user)

    await session.commit()
    return admin, analyst, user

async def create_sample_detections(session: AsyncSession, users: tuple[User, ...]):
    admin, analyst, user = users
    detection_types = ["image", "text", "multimodal"]
    threat_categories = ["malware", "phishing", "ransomware"]
    
    for user in [admin, analyst]:
        for i in range(5):  # 5 detections per user
            detection = ThreatDetection(
                user_id=user.id,
                detection_type=detection_types[i % len(detection_types)],
                content_path=f"/path/to/sample/content_{i}.txt",
                threat_score=0.25 + (i * 0.15),  # Varying threat scores
                confidence_score=0.7 + (i * 0.05),  # Varying confidence scores
                threat_category=threat_categories[i % len(threat_categories)],
                analysis_results={
                    "details": f"Sample analysis for detection #{i}",
                    "indicators": ["suspicious_pattern", "known_signature"],
                    "severity": "medium"
                },
                remediation_suggestions={
                    "actions": ["isolate", "analyze", "patch"],
                    "priority": "high",
                    "description": "Immediate action recommended"
                }
            )
            session.add(detection)
    
    await session.commit()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        users = await create_default_users(session)
        await create_sample_detections(session, users)
        print("Database initialized with default users and sample detections")

if __name__ == "__main__":
    asyncio.run(init_db()) 