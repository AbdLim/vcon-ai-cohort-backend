import logging
import uuid
import asyncio

logger = logging.getLogger(__name__)

class CloudinaryService:
    """
    A temporary stub service for Cloudinary file uploads.
    """
    
    @staticmethod
    async def upload_file(file_content: bytes, filename: str) -> str:
        """
        Simulates uploading a file to Cloudinary and returning a public URL.
        """
        logger.info(f"Simulating Cloudinary upload for {filename}...")
        await asyncio.sleep(1) # Simulate network delay
        
        # In a real scenario, this would use cloudinary.uploader.upload
        mock_id = str(uuid.uuid4())[:8]
        public_url = f"https://res.cloudinary.com/mock-cloud/video/upload/v1/{mock_id}/{filename}"
        
        logger.info(f"Mock upload complete: {public_url}")
        return public_url
