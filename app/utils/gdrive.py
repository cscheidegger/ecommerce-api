
import os
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from app.config import settings

logger = logging.getLogger(__name__)

def get_drive_service():
    """
    Get an authenticated Google Drive service
    """
    if not settings.GDRIVE_ENABLED:
        logger.warning("Google Drive integration is disabled")
        return None
    
    try:
        # The service account credentials should be stored securely
        # and accessed from environment variables or a secure vault
        service_account_info = json.loads(os.getenv("GDRIVE_CREDENTIALS", "{}"))
        
        # If no credentials are found, return None
        if not service_account_info:
            logger.error("No Google Drive credentials found")
            return None
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Error creating Google Drive service: {str(e)}")
        return None

def upload_file_to_drive(file_path, file_name, mime_type='application/octet-stream'):
    """
    Upload a file to Google Drive and return the URL
    """
    service = get_drive_service()
    if not service:
        return None
    
    try:
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Create a BytesIO object for the file data
        fh = BytesIO(file_data)
        
        # Set up file metadata
        file_metadata = {
            'name': file_name,
            'parents': [settings.GDRIVE_FOLDER_ID] if settings.GDRIVE_FOLDER_ID else []
        }
        
        # Create the media upload object
        media = MediaIoBaseUpload(fh, mimetype=mime_type, resumable=True)
        
        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        # Log and return the URL
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        logger.info(f"File uploaded to Google Drive: {file_name} (ID: {file_id})")
        return web_link
    
    except Exception as e:
        logger.error(f"Error uploading file to Google Drive: {str(e)}")
        return None

def create_quote_folder(quote_id):
    """
    Create a folder for a quote in Google Drive and return the URL
    """
    service = get_drive_service()
    if not service:
        return None
    
    try:
        # Set up folder metadata
        folder_name = f"Orçamento #{quote_id} - Proteus.lab"
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [settings.GDRIVE_FOLDER_ID] if settings.GDRIVE_FOLDER_ID else []
        }
        
        # Create the folder
        folder = service.files().create(
            body=folder_metadata,
            fields='id,webViewLink'
        ).execute()
        
        # Log and return the URL
        folder_id = folder.get('id')
        web_link = folder.get('webViewLink')
        logger.info(f"Folder created in Google Drive: {folder_name} (ID: {folder_id})")
        return {
            'id': folder_id,
            'url': web_link
        }
    
    except Exception as e:
        logger.error(f"Error creating folder in Google Drive: {str(e)}")
        return None
