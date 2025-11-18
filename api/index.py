"""Vercel serverless function handler for FastAPI"""
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.main import app
from mangum import Mangum

# Create handler for Vercel
handler = Mangum(app, lifespan="off")
