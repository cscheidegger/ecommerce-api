
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.routes.auth import get_current_active_user, get_current_admin_user
from app.services import auth as auth_service

router = APIRouter(tags=["users"], prefix="/users")

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update current user information.
    """
    # Get current user from DB
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    
    # Update fields if provided
    if user_update.username is not None:
        # Check if username is already taken
        existing_user = auth_service.get_user_by_username(db, user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        db_user.username = user_update.username
    
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = auth_service.get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        db_user.email = user_update.email
    
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    
    if user_update.password is not None:
        db_user.hashed_password = auth_service.get_password_hash(user_update.password)
    
    # Save changes
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Get all users (admin only).
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific user by ID (admin only).
    """
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/", response_model=User)
def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Create a new user (admin only).
    """
    # Check if username or email already exists
    db_user = auth_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    
    db_user = auth_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )
    
    # Create new user
    return auth_service.create_user(db, user)

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Update a user (admin only).
    """
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields (similar to update_user_me)
    if user_update.username is not None:
        existing_user = auth_service.get_user_by_username(db, user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400,
                detail="Username already registered",
            )
        db_user.username = user_update.username
    
    if user_update.email is not None:
        existing_user = auth_service.get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
        db_user.email = user_update.email
    
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    
    if user_update.password is not None:
        db_user.hashed_password = auth_service.get_password_hash(user_update.password)
    
    if user_update.is_admin is not None:
        db_user.is_admin = user_update.is_admin
    
    # Save changes
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Delete a user (admin only).
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own user account",
        )
    
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    
    return None
