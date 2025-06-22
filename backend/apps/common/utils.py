"""
Common utility functions for the FoodCam project.
"""

import os
import uuid
from django.utils.text import slugify
from django.core.files.storage import default_storage


def generate_unique_filename(instance, filename):
    """
    Generate a unique filename for uploaded files.
    
    Args:
        instance: The model instance
        filename: Original filename
        
    Returns:
        str: Unique filename with path
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', filename)


def generate_slug(text, max_length=50):
    """
    Generate a URL-friendly slug from text.
    
    Args:
        text (str): Text to convert to slug
        max_length (int): Maximum length of slug
        
    Returns:
        str: URL-friendly slug
    """
    return slugify(text)[:max_length]


def safe_delete_file(file_path):
    """
    Safely delete a file from storage.
    
    Args:
        file_path (str): Path to the file to delete
        
    Returns:
        bool: True if file was deleted, False otherwise
    """
    try:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            return True
    except Exception as e:
        # Log the error in production
        print(f"Error deleting file {file_path}: {e}")
    return False


def format_file_size(size_bytes):
    """
    Format file size in bytes to human readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}" 