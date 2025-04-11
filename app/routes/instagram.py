
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests

from app.database import get_db
from app.schemas.instagram import InstagramPost, InstagramPostList
from app.routes.auth import get_current_admin_user
from app.schemas.user import User
from app.config import settings

router = APIRouter(tags=["instagram"], prefix="/instagram")

# In-memory cache for Instagram posts (would use Redis in production)
cached_posts = []
last_updated = None

@router.get("/posts", response_model=List[InstagramPost])
def get_instagram_posts(
    skip: int = 0, 
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get Instagram posts from the Proteus.lab account.
    """
    # Return cached posts if available (in real implementation, we'd check cache TTL)
    if cached_posts:
        return cached_posts[skip:skip+limit]
    
    # If no posts in cache, return empty list
    # The posts will be populated by the Instagram service via the /update endpoint
    return []

@router.post("/update", status_code=200)
def update_instagram_feed(
    data: InstagramPostList,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update Instagram posts (called by the Instagram service).
    This would normally require API key authentication in production.
    """
    global cached_posts, last_updated
    
    # Update cache
    cached_posts = data.posts
    
    # In a production environment, we would:
    # 1. Validate the data
    # 2. Store posts in database
    # 3. Possibly generate notifications for new posts
    
    return {"success": True, "message": "Instagram feed updated", "post_count": len(data.posts)}

