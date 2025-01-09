from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = "https://uzgpjmvmoncwmfkbeknr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6Z3BqbXZtb25jd21ma2Jla25yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzYzMjA1NTAsImV4cCI6MjA1MTg5NjU1MH0.UXEuxEAzbRzS3sg9F_LWhrVZNuAEpPbU4L_FgxQ90Oc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper functions for common operations
async def get_user_by_email(email: str):
    response = supabase.table('users').select('*').eq('email', email).execute()
    return response.data[0] if response.data else None

async def get_user_by_username(username: str):
    response = supabase.table('users').select('*').eq('username', username).execute()
    return response.data[0] if response.data else None

async def create_user(user_data: dict):
    response = supabase.table('users').insert(user_data).execute()
    return response.data[0] if response.data else None

async def get_detections_by_user(user_id: str, limit: int = 100):
    response = supabase.table('detections').select('*').eq('user_id', user_id).limit(limit).execute()
    return response.data

async def create_detection(detection_data: dict):
    response = supabase.table('detections').insert(detection_data).execute()
    return response.data[0] if response.data else None 