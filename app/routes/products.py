
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from app.database import get_db
from app.models.product import Product as ProductModel
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.routes.auth import get_current_active_user, get_current_admin_user
from app.schemas.user import User
from app.config import settings

router = APIRouter(tags=["products"], prefix="/products")

@router.get("/", response_model=List[Product])
def get_products(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all products with optional filtering by category.
    """
    query = db.query(ProductModel)
    if category:
        query = query.filter(ProductModel.category == category)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=Product)
def create_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image: Optional[UploadFile] = File(None),
    model_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new product (admin only).
    """
    # Create product data
    product_data = {
        "title": title,
        "description": description,
        "price": price,
        "category": category,
    }
    
    # Handle image upload
    if image:
        image_path = save_upload_file(image, "images")
        product_data["image"] = image_path
    
    # Handle 3D model upload
    if model_file:
        model_path = save_upload_file(model_file, "models")
        product_data["model_file"] = model_path
    
    # Create and save product
    db_product = ProductModel(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    model_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a product (admin only).
    """
    # Get existing product
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields if provided
    if title:
        db_product.title = title
    if description:
        db_product.description = description
    if price:
        db_product.price = price
    if category:
        db_product.category = category
    
    # Handle image upload
    if image:
        if db_product.image:
            delete_file(db_product.image)
        image_path = save_upload_file(image, "images")
        db_product.image = image_path
    
    # Handle 3D model upload
    if model_file:
        if db_product.model_file:
            delete_file(db_product.model_file)
        model_path = save_upload_file(model_file, "models")
        db_product.model_file = model_path
    
    # Save changes
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a product (admin only).
    """
    # Get product
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete associated files
    if db_product.image:
        delete_file(db_product.image)
    if db_product.model_file:
        delete_file(db_product.model_file)
    
    # Delete product
    db.delete(db_product)
    db.commit()
    return None

# Utility functions for file handling
def save_upload_file(upload_file: UploadFile, subfolder: str) -> str:
    """Save an uploaded file and return its path."""
    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, upload_file.filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    
    # Return the path relative to the upload directory
    return os.path.join(subfolder, upload_file.filename)

def delete_file(file_path: str) -> None:
    """Delete a file if it exists."""
    full_path = os.path.join(settings.UPLOAD_DIR, file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
