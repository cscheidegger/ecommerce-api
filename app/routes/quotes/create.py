
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from app.database import get_db
from app.models.quote import Quote as QuoteModel, QuoteStatus
from app.schemas.quote import QuoteResponse
from app.routes.auth import get_current_active_user
from app.schemas.user import User
from app.config import settings
from app.utils.email import send_quote_notification, send_advanced_quote_notification
from app.utils.gdrive import create_quote_folder, upload_file_to_drive
from app.utils.file import save_upload_file
from app.routes.quotes.utils import handle_file_uploads, setup_drive_folder

router = APIRouter()

@router.post("/", response_model=QuoteResponse)
async def create_quote(
    description: str = Form(...),
    files: List[UploadFile] = File([]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new quote request.
    """
    # Save uploaded files
    saved_files = await handle_file_uploads(files)
    
    # Create quote
    db_quote = QuoteModel(
        user_id=current_user.id,
        description=description,
        files=saved_files,
        status=QuoteStatus.pending
    )
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    # Create Google Drive folder if enabled
    drive_url = await setup_drive_folder(db_quote, saved_files, db)
    
    # Send email notification
    quote_data = {
        'id': db_quote.id,
        'description': description,
        'status': db_quote.status,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'drive_url': drive_url
    }
    send_quote_notification(quote_data)
    
    return {
        "id": db_quote.id,
        "message": "Quote request submitted successfully",
        "status": db_quote.status,
        "drive_url": drive_url
    }

@router.post("/advanced", response_model=QuoteResponse)
async def create_advanced_quote(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    company: str = Form(None),
    material: str = Form(...),
    finish: str = Form(...),
    quantity: int = Form(...),
    deadline: str = Form(...),
    application: str = Form(...),
    comments: str = Form(None),
    files: List[UploadFile] = File(...),
    current_user: Optional[User] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new advanced quote request with detailed information.
    """
    # Save uploaded files
    saved_files = await handle_file_uploads(files)
    
    # Prepare description with all the details
    description = f"""
    Nome: {name}
    Email: {email}
    Telefone: {phone}
    Empresa: {company or 'Não informado'}
    
    Material: {material}
    Acabamento: {finish}
    Quantidade: {quantity}
    Prazo: {deadline}
    Aplicação: {application}
    
    Observações: {comments or 'Sem observações adicionais'}
    """
    
    # Create quote record
    db_quote = QuoteModel(
        user_id=current_user.id if current_user else None,
        description=description,
        files=saved_files,
        status=QuoteStatus.pending,
        metadata={
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "material": material,
            "finish": finish,
            "quantity": quantity,
            "deadline": deadline,
            "application": application
        }
    )
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    # Create Google Drive folder if enabled
    drive_url = await setup_drive_folder(db_quote, saved_files, db)
    
    # Send email notification
    quote_data = {
        'id': db_quote.id,
        'name': name,
        'email': email,
        'phone': phone,
        'company': company,
        'material': material,
        'finish': finish,
        'quantity': quantity,
        'deadline': deadline,
        'application': application,
        'comments': comments,
        'num_files': len(saved_files),
        'status': db_quote.status,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'drive_url': drive_url
    }
    send_advanced_quote_notification(quote_data)
    
    return {
        "id": db_quote.id,
        "message": "Quote request submitted successfully",
        "status": db_quote.status,
        "drive_url": drive_url
    }
