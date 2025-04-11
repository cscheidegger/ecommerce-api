
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.order import Order as OrderModel, OrderStatus
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderWithItems
from app.routes.auth import get_current_active_user, get_current_admin_user
from app.schemas.user import User
from app.services import order as order_service

router = APIRouter(tags=["orders"], prefix="/orders")

@router.get("/", response_model=List[Order])
def get_orders(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders for the current user, or all orders for admin.
    """
    if current_user.is_admin:
        query = db.query(OrderModel)
        if status:
            query = query.filter(OrderModel.status == status)
        orders = query.offset(skip).limit(limit).all()
    else:
        query = db.query(OrderModel).filter(OrderModel.user_id == current_user.id)
        if status:
            query = query.filter(OrderModel.status == status)
        orders = query.offset(skip).limit(limit).all()
    
    return orders

@router.get("/{order_id}", response_model=OrderWithItems)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific order by ID.
    """
    # Get order
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user is allowed to view the order
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this order")
    
    return order

@router.post("/", response_model=Order)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order.
    """
    return order_service.create_order(db, order_data, current_user.id)

@router.put("/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update an order (admin only).
    """
    # Get order
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update status if provided
    if order_update.status:
        order.status = order_update.status
    
    # Save changes
    db.commit()
    db.refresh(order)
    
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an order (can be done by the owner or admin).
    """
    # Get order
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user is allowed to cancel the order
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
    
    # Can only cancel if it's pending or processing
    if order.status not in [OrderStatus.pending, OrderStatus.processing]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel order with status {order.status}"
        )
    
    # Set status to cancelled
    order.status = OrderStatus.cancelled
    db.commit()
    
    return None
