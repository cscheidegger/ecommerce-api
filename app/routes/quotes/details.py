
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quote import Quote as QuoteModel
from app.schemas.quote import Quote
from app.routes.auth import get_current_active_user
from app.schemas.user import User

router = APIRouter()

@router.get("/{quote_id}", response_model=Quote)
def get_quote(
    quote_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific quote by ID.
    """
    # Get quote
    quote = db.query(QuoteModel).filter(QuoteModel.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user is allowed to view the quote
    if not current_user.is_admin and quote.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this quote")
    
    return quote
