from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Threat Detection API"
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:MALICIOUSDETECTION2025@db.uzgpjmvmoncwmfkbeknr.supabase.co:5432/postgres"
    
    # Supabase Configuration
    SUPABASE_URL: str = "https://uzgpjmvmoncwmfkbeknr.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6Z3BqbXZtb25jd21ma2Jla25yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzYzMjA1NTAsImV4cCI6MjA1MTg5NjU1MH0.UXEuxEAzbRzS3sg9F_LWhrVZNuAEpPbU4L_FgxQ90Oc"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        case_sensitive = True

settings = Settings() 