import logging
import cloudinary
import cloudinary.uploader
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure cloudinary using the settings URL
import os
from urllib.parse import urlparse

if settings.CLOUDINARY_URL:
    try:
        # Expected format: cloudinary://api_key:api_secret@cloud_name
        parsed_url = urlparse(settings.CLOUDINARY_URL)
        cloudinary.config(
            cloud_name=parsed_url.hostname,
            api_key=parsed_url.username,
            api_secret=parsed_url.password,
            secure=True
        )
    except Exception as e:
        logger.error(f"Failed to parse CLOUDINARY_URL: {e}")

class CloudinaryService:
    """
    Service for uploading files and managing assets on Cloudinary.
    """
    
    @staticmethod
    def upload_file_from_path(filepath: str, filename: str = None) -> str:
        """
        Uploads a file to Cloudinary from a local filepath and returns the public URL.
        """
        logger.info(f"Uploading file {filepath} to Cloudinary...")
        
        # Upload the file
        # resource_type="auto" allows video, image, and raw files to be handled.
        try:
            response = cloudinary.uploader.upload(
                filepath, 
                resource_type="auto",
                public_id=filename,
                use_filename=True,
                unique_filename=True
            )
            
            public_url = response.get("secure_url")
            logger.info(f"Upload complete: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise

    @staticmethod
    def upload_file_from_url(url: str, filename: str = None) -> str:
        """
        Uploads a file to Cloudinary from a public URL and returns the secure URL.
        """
        logger.info(f"Uploading file from URL {url} to Cloudinary...")
        try:
            kwargs = {
                "resource_type": "auto",
            }
            if filename:
                kwargs["public_id"] = filename
                kwargs["use_filename"] = True
                kwargs["unique_filename"] = True
                
            response = cloudinary.uploader.upload(url, **kwargs)
            
            public_url = response.get("secure_url")
            logger.info(f"Upload complete: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Cloudinary upload from URL failed: {e}")
            raise
