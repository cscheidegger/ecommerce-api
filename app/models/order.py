
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class OrderStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total = Column(Float)
    customer_info = Column(JSON)  # Store name, email, address as JSON
    payment_method = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("OrderItem", back_populates="order")
    user = relationship("User")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    quantity = Column(Integer)
    price = Column(Float)  # Price at the time of order
    custom_data = Column(JSON, nullable=True)  # For custom maps, etc.
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    service = relationship("Service")
