import pytest
import os
os.environ["DATABASE_URL"] = "sqlite:///test.db"

from fastapi.testclient import TestClient
from main import app, Base, engine

# Setup test client
client = TestClient(app)

# Create tables before tests
Base.metadata.create_all(engine)

# ==================
# UNIT TESTS
# ==================

def test_price_validation_rejects_negative():
    """Unit test - price validator rejects negative values"""
    from main import ItemDTO
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ItemDTO(name="Test", price=-10)

def test_price_validation_rejects_zero():
    """Unit test - price validator rejects zero"""
    from main import ItemDTO
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ItemDTO(name="Test", price=0)

def test_price_validation_accepts_positive():
    """Unit test - price validator accepts positive values"""
    from main import ItemDTO
    item = ItemDTO(name="Test", price=99.99)
    assert item.price == 99.99

# ==================
# INTEGRATION TESTS
# ==================

def test_home_endpoint():
    """Integration test - home endpoint returns 200"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "API is running"

def test_signup_success():
    """Integration test - user can sign up successfully"""
    import time
    email = f"testuser{int(time.time())}@example.com"
    response = client.post("/auth/signup", json={
        "email": email,
        "password": "testpassword123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == email

def test_signup_duplicate_email():
    """Integration test - duplicate email returns 400"""
    client.post("/auth/signup", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    response = client.post("/auth/signup", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    assert response.status_code == 400

def test_login_success():
    """Integration test - user can login with correct credentials"""
    client.post("/auth/signup", json={
        "email": "logintest@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "email": "logintest@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_without_token():
    """Integration test - protected route returns 401 without token"""
    response = client.get("/protected")
    assert response.status_code == 401