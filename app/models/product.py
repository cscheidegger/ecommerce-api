
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    category = Column(String, index=True)
    image = Column(String)  # URL or path to image
    model_file = Column(String, nullable=True)  # Path to 3D model file
    rating_sum = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def rating(self):
        if self.rating_count == 0:
            return 0
        return self.rating_sum / self.rating_count
