
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime
from app.models.order import OrderStatus

# OrderItem schemas
class OrderItemBase(BaseModel):
    product_id: Optional[int] = None
    service_id: Optional[int] = None
    quantity: int
    price: float
    custom_data: Optional[Dict] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    
    class Config:
        orm_mode = True

# Order schemas
class OrderBase(BaseModel):
    customer_info: Dict[str, str] = Field(..., example={
        "name": "John Doe",
        "email": "john@example.com",
        "address": "123 Main St, City"
    })
    payment_method: str

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    total: float
    created_at: datetime
    
    class Config:
        orm_mode = True

class OrderWithItems(Order):
    items: List[OrderItem]
    
    class Config:
        orm_mode = True
