# prompts/services.py

import os
import uuid
import base64
import requests
from django.conf      import settings
from django.core.files.base import ContentFile


class ImageGenerationService:
    """
    Handles all communication with external
    AI image generation API.
    Keeps API logic separate from views.
    """

    def __init__(self):
        self.api_key = settings.IMAGE_GEN_API_KEY
        self.api_url = settings.IMAGE_GEN_API_URL

    def generate(self, prompt_text):
        """
        Sends prompt to API → returns image as Django ContentFile
        
        Returns:
            success: True/False
            image_file: ContentFile or None
            error: error message or None
        """

        if not self.api_key:
            return {
                'success': False,
                'error'  : 'API key not configured'
            }

        try:
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type' : 'application/json',
                    'Accept'       : 'application/json',
                },
                json={
                    'text_prompts': [
                        {
                            'text'  : prompt_text,
                            'weight': 1
                        }
                    ],
                    'cfg_scale'    : 7,
                    'height'       : 1024,
                    'width'        : 1024,
                    'steps'        : 30,
                    'samples'      : 1,
                },
                timeout=60   # 60 second timeout
            )

            # Handle API errors
            if response.status_code == 401:
                return {
                    'success': False,
                    'error'  : 'Invalid API key'
                }
            elif response.status_code == 429:
                return {
                    'success': False,
                    'error'  : 'API rate limit exceeded. Try again later.'
                }
            elif response.status_code == 402:
                return {
                    'success': False,
                    'error'  : 'Insufficient API credits'
                }
            elif response.status_code != 200:
                return {
                    'success': False,
                    'error'  : f'API error: {response.status_code}'
                }

            # Parse response
            data = response.json()

            # Stability AI returns base64 encoded image
            image_b64  = data['artifacts'][0]['base64']
            image_data = base64.b64decode(image_b64)

            # Create unique filename
            filename   = f"generated/{uuid.uuid4().hex}.png"
            image_file = ContentFile(image_data, name=filename)

            return {
                'success'   : True,
                'image_file': image_file,
                'error'     : None
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error'  : 'Request timed out. Please try again.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error'  : 'Could not connect to image API.'
            }
        except (KeyError, IndexError):
            return {
                'success': False,
                'error'  : 'Unexpected API response format.'
            }
        except Exception as e:
            return {
                'success': False,
                'error'  : f'Unexpected error: {str(e)}'
            }