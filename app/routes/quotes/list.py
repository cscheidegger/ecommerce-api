
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.quote import Quote as QuoteModel, QuoteStatus
from app.schemas.quote import Quote
from app.routes.auth import get_current_active_user
from app.schemas.user import User

router = APIRouter()

@router.get("/", response_model=List[Quote])
def get_quotes(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[QuoteStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all quotes for the current user, or all quotes for admin.
    """
    if current_user.is_admin:
        query = db.query(QuoteModel)
        if status:
            query = query.filter(QuoteModel.status == status)
        quotes = query.offset(skip).limit(limit).all()
    else:
        query = db.query(QuoteModel).filter(QuoteModel.user_id == current_user.id)
        if status:
            query = query.filter(QuoteModel.status == status)
        quotes = query.offset(skip).limit(limit).all()
    
    return quotes
