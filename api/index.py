"""Vercel serverless function handler for FastAPI"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)

from app.main import app
from mangum import Mangum

# Create Mangum handler for ASGI application
handler = Mangum(app, lifespan="off")
