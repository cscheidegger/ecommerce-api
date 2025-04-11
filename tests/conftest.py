
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.services.auth import get_password_hash
from app.models.user import User

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for testing
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        
        # Tear down the database after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client using the FastAPI app
    with TestClient(app) as c:
        yield c
    
    # Remove the override after the test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    # Create a test user
    hashed_password = get_password_hash("password123")
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=hashed_password,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@pytest.fixture(scope="function")
def test_admin(db):
    # Create a test admin user
    hashed_password = get_password_hash("adminpass")
    admin = User(
        username="testadmin",
        email="admin@example.com",
        full_name="Test Admin",
        hashed_password=hashed_password,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return admin


@pytest.fixture(scope="function")
def user_token(client, test_user):
    # Get a token for the test user
    login_data = {
        "username": test_user.username,
        "password": "password123"
    }
    response = client.post("/api/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    return token


@pytest.fixture(scope="function")
def admin_token(client, test_admin):
    # Get a token for the test admin
    login_data = {
        "username": test_admin.username,
        "password": "adminpass"
    }
    response = client.post("/api/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    return token
