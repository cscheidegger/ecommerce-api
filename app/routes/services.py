
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.service import Service as ServiceModel
from app.schemas.service import Service, ServiceCreate, ServiceUpdate
from app.routes.auth import get_current_active_user, get_current_admin_user
from app.schemas.user import User

router = APIRouter(tags=["services"], prefix="/services")

@router.get("/", response_model=List[Service])
def get_services(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all services with optional filtering by category.
    """
    query = db.query(ServiceModel)
    if category:
        query = query.filter(ServiceModel.category == category)
    
    services = query.offset(skip).limit(limit).all()
    return services

@router.get("/{service_id}", response_model=Service)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """
    Get a specific service by ID.
    """
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=Service)
def create_service(
    service: ServiceCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new service (admin only).
    """
    db_service = ServiceModel(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.put("/{service_id}", response_model=Service)
def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a service (admin only).
    """
    db_service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Update fields if provided
    update_data = service_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a service (admin only).
    """
    db_service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db.delete(db_service)
    db.commit()
    return None
