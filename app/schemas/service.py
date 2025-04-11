
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Shared properties
class ServiceBase(BaseModel):
    name: str
    description: str
    base_price: float
    category: str

# Properties to receive on service creation
class ServiceCreate(ServiceBase):
    pass

# Properties to receive on service update
class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    category: Optional[str] = None

# Properties to return to client
class Service(ServiceBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
