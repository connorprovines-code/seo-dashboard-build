"""
Integration tests to verify all modules work together.
Run with: pytest backend/tests/test_integration.py
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test that API is running"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_user_registration_and_login():
    """Test user can register and login"""
    # Register
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test@example.com"

    # Login
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

    return response.json()["access_token"]


def test_project_creation():
    """Test project CRUD"""
    # Get token
    token = test_user_registration_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # Create project
    response = client.post("/api/projects", json={
        "name": "Test Blog",
        "domain": "testblog.com"
    }, headers=headers)
    assert response.status_code == 201
    project = response.json()
    assert project["name"] == "Test Blog"
    assert project["domain"] == "testblog.com"

    project_id = project["id"]

    # List projects
    response = client.get("/api/projects", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Get project
    response = client.get(f"/api/projects/{project_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == project_id

    return project_id, token


def test_keyword_operations():
    """Test keyword CRUD"""
    project_id, token = test_project_creation()
    headers = {"Authorization": f"Bearer {token}"}

    # Add keyword
    response = client.post(f"/api/projects/{project_id}/keywords", json={
        "keyword_text": "seo tools"
    }, headers=headers)
    assert response.status_code == 201
    keyword = response.json()
    assert keyword["keyword_text"] == "seo tools"

    # Bulk add
    response = client.post(f"/api/projects/{project_id}/keywords/bulk", json={
        "keywords": ["content marketing", "link building", "rank tracking"]
    }, headers=headers)
    assert response.status_code == 201
    assert response.json()["added"] == 3

    # List keywords
    response = client.get(f"/api/projects/{project_id}/keywords", headers=headers)
    assert response.status_code == 200
    keywords = response.json()
    assert len(keywords) == 4


def test_competitors_operations():
    """Test competitor management"""
    project_id, token = test_project_creation()
    headers = {"Authorization": f"Bearer {token}"}

    # Add competitor
    response = client.post(f"/api/projects/{project_id}/competitors", json={
        "domain": "competitor.com",
        "notes": "Main competitor"
    }, headers=headers)
    assert response.status_code == 201
    competitor = response.json()
    assert competitor["domain"] == "competitor.com"

    # List competitors
    response = client.get(f"/api/projects/{project_id}/competitors", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_api_routes_exist():
    """Test that all API routes are registered"""
    routes = [route.path for route in app.routes]

    # Core routes
    assert "/health" in routes
    assert "/api/auth/register" in routes
    assert "/api/auth/login" in routes

    # Project routes
    assert "/api/projects" in routes

    # Feature routes
    assert "/api/projects/{project_id}/keywords" in routes
    assert "/api/projects/{project_id}/rank-tracking" in routes
    assert "/api/projects/{project_id}/competitors" in routes
    assert "/api/projects/{project_id}/backlinks/summary" in routes

    # AI routes
    assert "/api/ai/chat" in routes
    assert "/api/ai/analyze/keywords" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
