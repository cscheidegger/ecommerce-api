
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quote import Quote as QuoteModel
from app.schemas.quote import Quote, QuoteUpdate
from app.routes.auth import get_current_active_user, get_current_admin_user
from app.schemas.user import User
from app.utils.file import delete_upload_file

router = APIRouter()

@router.put("/{quote_id}", response_model=Quote)
def update_quote(
    quote_id: int,
    quote_update: QuoteUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Review and update a quote (admin only).
    """
    # Get quote
    quote = db.query(QuoteModel).filter(QuoteModel.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Update fields
    if quote_update.status is not None:
        quote.status = quote_update.status
    
    if quote_update.estimated_price is not None:
        quote.estimated_price = quote_update.estimated_price
    
    if quote_update.admin_notes is not None:
        quote.admin_notes = quote_update.admin_notes
    
    if quote_update.drive_url is not None:
        quote.drive_url = quote_update.drive_url
    
    # Save changes
    db.commit()
    db.refresh(quote)
    
    return quote

@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a quote (can be done by the owner or admin).
    """
    # Get quote
    quote = db.query(QuoteModel).filter(QuoteModel.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user is allowed to delete the quote
    if not current_user.is_admin and quote.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this quote")
    
    # Delete associated files
    for file_path in quote.files:
        delete_upload_file(file_path)
    
    # Delete quote
    db.delete(quote)
    db.commit()
    
    return None
