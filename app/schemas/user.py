
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = False

# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties to return to client
class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Additional properties stored in DB
class UserInDB(User):
    hashed_password: str
    
    class Config:
        orm_mode = True
