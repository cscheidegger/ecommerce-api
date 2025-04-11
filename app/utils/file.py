
import os
import uuid
from fastapi import UploadFile, HTTPException
from app.config import settings

def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Check if the file has an allowed extension."""
    ext = os.path.splitext(filename)[1].lower()
    if not ext in allowed_extensions:
        return False
    return True

def generate_unique_filename(filename: str) -> str:
    """Generate a unique filename to prevent overwrites."""
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    return unique_filename

async def save_upload_file(
    upload_file: UploadFile, 
    subfolder: str,
    allowed_extensions: list = None
) -> str:
    """
    Save an uploaded file and return its path.
    
    Args:
        upload_file: The file to save
        subfolder: The subfolder within the uploads directory
        allowed_extensions: List of allowed file extensions
        
    Returns:
        The relative path to the saved file
    """
    # Check file size
    content = await upload_file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB"
        )
    
    # Check file extension if provided
    if allowed_extensions:
        if not validate_file_extension(upload_file.filename, allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
    
    # Use a unique filename to prevent overwrites
    unique_filename = generate_unique_filename(upload_file.filename)
    
    # Create directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return the path relative to the uploads directory
    return os.path.join(subfolder, unique_filename)

def delete_upload_file(file_path: str) -> bool:
    """
    Delete an uploaded file.
    
    Args:
        file_path: The path relative to the uploads directory
        
    Returns:
        True if file was deleted, False otherwise
    """
    full_path = os.path.join(settings.UPLOAD_DIR, file_path)
    
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    
    return False
