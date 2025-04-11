
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

# Shared properties
class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    category: str
    image: Optional[str] = None

# Properties to receive on product creation
class ProductCreate(ProductBase):
    model_file: Optional[str] = None

# Properties to receive on product update
class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image: Optional[str] = None
    model_file: Optional[str] = None

# Properties to return to client
class Product(ProductBase):
    id: int
    model_file: Optional[str] = None
    rating: float
    created_at: datetime
    
    class Config:
        orm_mode = True
        
# Properties to return with rating details
class ProductWithRating(Product):
    rating_detail: Dict[str, int] = {"rate": 0, "count": 0}
    
    class Config:
        orm_mode = True
