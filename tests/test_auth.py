
import pytest
from fastapi.testclient import TestClient

def test_register(client):
    """Test user registration."""
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpassword",
        "full_name": "New User"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data

def test_login(client, test_user):
    """Test user login."""
    login_data = {
        "username": test_user.username,
        "password": "password123"
    }
    
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    login_data = {
        "username": test_user.username,
        "password": "wrongpassword"
    }
    
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401

def test_login_wrong_username(client):
    """Test login with non-existent username."""
    login_data = {
        "username": "nonexistentuser",
        "password": "password123"
    }
    
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401
