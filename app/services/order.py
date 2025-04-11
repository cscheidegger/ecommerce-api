
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderCreate
from app.models.product import Product
from app.models.service import Service
from fastapi import HTTPException

def create_order(db: Session, order_data: OrderCreate, user_id: int):
    """Create an order with its items."""
    # Calculate total
    total = calculate_order_total(db, order_data)
    
    # Create order
    db_order = Order(
        user_id=user_id,
        total=total,
        customer_info=order_data.customer_info,
        payment_method=order_data.payment_method,
        status=OrderStatus.pending
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    create_order_items(db, db_order.id, order_data.items)
    
    # Refresh order with items
    db.refresh(db_order)
    return db_order

def calculate_order_total(db: Session, order_data: OrderCreate) -> float:
    """Calculate the total price of an order."""
    total = 0.0
    
    for item in order_data.items:
        # Validate that product or service exists
        if item.product_id:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            price = product.price
        elif item.service_id:
            service = db.query(Service).filter(Service.id == item.service_id).first()
            if not service:
                raise HTTPException(status_code=404, detail=f"Service {item.service_id} not found")
            price = service.base_price
        else:
            raise HTTPException(status_code=400, detail="Item must have either product_id or service_id")
        
        # Add item price to total
        total += price * item.quantity
    
    return total

def create_order_items(db: Session, order_id: int, items_data):
    """Create order items for an order."""
    for item_data in items_data:
        db_item = OrderItem(
            order_id=order_id,
            product_id=item_data.product_id,
            service_id=item_data.service_id,
            quantity=item_data.quantity,
            price=item_data.price,
            custom_data=item_data.custom_data
        )
        db.add(db_item)
    
    db.commit()
