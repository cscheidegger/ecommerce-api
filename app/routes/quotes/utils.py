
from fastapi import UploadFile
from sqlalchemy.orm import Session
import os
from typing import List

from app.utils.file import save_upload_file
from app.utils.gdrive import create_quote_folder, upload_file_to_drive
from app.config import settings
from app.models.quote import Quote as QuoteModel

async def handle_file_uploads(files: List[UploadFile]) -> List[str]:
    """
    Process and save uploaded files
    
    Args:
        files: List of uploaded files
        
    Returns:
        List of saved file paths
    """
    saved_files = []
    for file in files:
        file_path = await save_upload_file(
            file, 
            "quotes",
            allowed_extensions=['.stl', '.obj', '.3mf']
        )
        saved_files.append(file_path)
    
    return saved_files

async def setup_drive_folder(quote: QuoteModel, saved_files: List[str], db: Session) -> str:
    """
    Set up Google Drive folder for quote files if enabled
    
    Args:
        quote: The quote model instance
        saved_files: List of saved file paths
        db: Database session
        
    Returns:
        Google Drive URL or None
    """
    drive_url = None
    if settings.GDRIVE_ENABLED:
        folder_info = create_quote_folder(quote.id)
        if folder_info:
            drive_url = folder_info['url']
            quote.drive_url = drive_url
            
            # Upload files to the Google Drive folder
            for file_path in saved_files:
                full_path = os.path.join(settings.UPLOAD_DIR, file_path)
                file_name = os.path.basename(file_path)
                upload_file_to_drive(full_path, file_name)
            
            db.commit()
    
    return drive_url
