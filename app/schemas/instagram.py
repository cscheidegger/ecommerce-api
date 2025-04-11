
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InstagramPost(BaseModel):
    """Schema for an Instagram post."""
    id: str
    image_url: str
    caption: str
    likes: int
    timestamp: str
    
    class Config:
        orm_mode = True

class InstagramPostList(BaseModel):
    """Schema for a list of Instagram posts."""
    posts: List[InstagramPost]
    
    class Config:
        orm_mode = True

