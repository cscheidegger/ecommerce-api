
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Union

from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.token import TokenPayload
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constants
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(
    user_id: Union[str, int], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a new JWT token."""
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    db: Session, token: str, credentials_exception: HTTPException
) -> Optional[User]:
    """Get the current user from a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
        user_id = token_data.sub
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    return user
