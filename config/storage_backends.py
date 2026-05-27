"""
Supabase Storage Backend for Django
Handles file uploads to Supabase Storage via REST API
"""
import os
from django.core.files.storage import Storage
from django.conf import settings
import requests
from io import BytesIO


class SupabaseStorage(Storage):
    """Custom storage backend for Supabase"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.bucket_name = os.getenv('SUPABASE_BUCKET', 'media')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

    def _get_headers(self):
        """Get authorization headers for Supabase API"""
        return {
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
        }

    def _get_file_headers(self):
        """Get headers for file upload (without Content-Type, let requests handle it)"""
        return {
            'Authorization': f'Bearer {self.supabase_key}',
        }

    def _save(self, name, content):
        """Save file to Supabase Storage"""
        # Read file content
        if hasattr(content, 'read'):
            file_content = content.read()
        else:
            file_content = content

        # Upload URL
        upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{name}"

        try:
            response = requests.post(
                upload_url,
                headers=self._get_file_headers(),
                data=file_content
            )
            response.raise_for_status()
            return name
        except requests.exceptions.RequestException as e:
            raise IOError(f"Failed to save file to Supabase: {str(e)}")

    def _open(self, name, mode='rb'):
        """Open/download file from Supabase Storage"""
        file_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"
        
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.exceptions.RequestException as e:
            raise IOError(f"Failed to open file from Supabase: {str(e)}")

    def delete(self, name):
        """Delete file from Supabase Storage"""
        delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{name}"
        
        try:
            response = requests.delete(
                delete_url,
                headers=self._get_headers()
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise IOError(f"Failed to delete file from Supabase: {str(e)}")

    def exists(self, name):
        """Check if file exists in Supabase Storage"""
        file_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"
        try:
            response = requests.head(file_url)
            return response.status_code == 200
        except:
            return False

    def url(self, name):
        """Return the public URL for a file"""
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"

    def get_accessed_time(self, name):
        """Not implemented for Supabase"""
        raise NotImplementedError("Supabase Storage does not provide access time")

    def get_created_time(self, name):
        """Not implemented for Supabase"""
        raise NotImplementedError("Supabase Storage does not provide creation time")

    def get_modified_time(self, name):
        """Not implemented for Supabase"""
        raise NotImplementedError("Supabase Storage does not provide modified time")

    def listdir(self, path):
        """List directory contents"""
        raise NotImplementedError("Directory listing not implemented for Supabase")

    def size(self, name):
        """Get file size"""
        raise NotImplementedError("File size retrieval not implemented for Supabase")
