
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.quote import QuoteStatus

# Quote schemas
class QuoteBase(BaseModel):
    description: str
    files: List[str]

class QuoteCreate(QuoteBase):
    pass

class AdvancedQuoteCreate(BaseModel):
    name: str
    email: str
    phone: str
    company: Optional[str] = None
    material: str
    finish: str
    quantity: int
    deadline: str
    application: str
    comments: Optional[str] = None
    files: List[str]

class QuoteUpdate(BaseModel):
    status: Optional[QuoteStatus] = None
    estimated_price: Optional[float] = None
    admin_notes: Optional[str] = None
    drive_url: Optional[str] = None

class Quote(QuoteBase):
    id: int
    user_id: Optional[int] = None
    status: QuoteStatus
    estimated_price: Optional[float] = None
    admin_notes: Optional[str] = None
    drive_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class QuoteResponse(BaseModel):
    id: int
    message: str
    status: QuoteStatus
    drive_url: Optional[str] = None
