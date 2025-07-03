import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import io
from typing import Optional, Tuple

class UploadService:
    def __init__(self, upload_folder: str = "uploads", max_file_size: int = 5 * 1024 * 1024):
        self.upload_folder = upload_folder
        self.max_file_size = max_file_size
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_image(self, file_data: bytes) -> bool:
        """Validate that the file is actually an image"""
        try:
            image = Image.open(io.BytesIO(file_data))
            image.verify()
            return True
        except Exception:
            return False
    
    def resize_image(self, file_data: bytes, max_width: int = 1200, max_height: int = 1200) -> bytes:
        """Resize image to maximum dimensions while maintaining aspect ratio"""
        try:
            image = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Calculate new dimensions
            width, height = image.size
            if width > max_width or height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception:
            return file_data  # Return original if resize fails
    
    def save_image(self, file_data: bytes, original_filename: str) -> Optional[str]:
        """Save image file and return the file path"""
        if not self.validate_image(file_data):
            return None
        
        if len(file_data) > self.max_file_size:
            return None
        
        # Generate unique filename
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Resize image
        resized_data = self.resize_image(file_data)
        
        # Save file
        file_path = os.path.join(self.upload_folder, unique_filename)
        try:
            with open(file_path, 'wb') as f:
                f.write(resized_data)
            return unique_filename
        except Exception:
            return None
    
    def get_file_url(self, filename: str, base_url: str = "") -> str:
        """Get full URL for uploaded file"""
        return f"{base_url}/uploads/{filename}"
    
    def delete_file(self, filename: str) -> bool:
        """Delete uploaded file"""
        try:
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False 