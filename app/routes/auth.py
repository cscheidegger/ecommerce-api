
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app.database import get_db
from app.services import auth as auth_service
from app.schemas.user import User, UserCreate
from app.schemas.token import Token

router = APIRouter(tags=["authentication"], prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=User)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register a new user.
    """
    user = auth_service.get_user_by_email(db, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    
    user = auth_service.get_user_by_username(db, username=user_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists.",
        )
    
    return auth_service.create_user(db, user_data)

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Get an access token for future requests.
    """
    user = auth_service.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        user_id=user.id, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get current user
def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = auth_service.get_current_user(db, token, credentials_exception)
    return user

# Dependency to get current active user
def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

# Dependency to get current admin user
def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions"
        )
    return current_user
