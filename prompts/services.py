# prompts/services.py

import io
import base64
import requests
from django.conf import settings
from PIL import Image


class ImageToImageService:
    """
    Takes user uploaded JPG + prompt text
    Sends to Stability AI img2img API
    Returns transformed image as bytes
    Image is NOT saved to database
    """

    def __init__(self):
        self.api_key = settings.IMAGE_GEN_API_KEY
        self.api_url = settings.IMAGE_GEN_API_URL

    def transform(self, image_file, prompt_text, strength=0.7):
        """
        image_file   : InMemoryUploadedFile (JPG)
        prompt_text  : transformation description
        strength     : 0.1 (subtle) to 1.0 (total change)

        Returns:
            success    : True/False
            image_b64  : base64 string of result image
            error      : error message or None
        """

        if not self.api_key:
            return {
                'success': False,
                'error'  : 'API key not configured'
            }

        try:
            # ── Prepare image ─────────────────────────────────────────────
            # Open and resize to 1024x1024 (required by Stability AI)
            img = Image.open(image_file)

            # Convert to RGB (removes alpha channel if PNG sneaks in)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize maintaining aspect ratio
            img = img.resize((1024, 1024), Image.LANCZOS)

            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)

            # ── Call Stability AI img2img API ─────────────────────────────
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Accept'       : 'application/json',
                },
                files={
                    'init_image': ('image.jpg', img_bytes, 'image/jpeg'),
                },
                data={
                    'text_prompts[0][text]'  : prompt_text,
                    'text_prompts[0][weight]': '1',
                    'image_strength'         : str(strength),
                    'cfg_scale'              : '7',
                    'samples'                : '1',
                    'steps'                  : '30',
                },
                timeout=60
            )

            # ── Handle errors ─────────────────────────────────────────────
            if response.status_code == 401:
                return {'success': False, 'error': 'Invalid API key'}

            elif response.status_code == 429:
                return {'success': False, 'error': 'Rate limit exceeded. Try again later.'}

            elif response.status_code == 402:
                return {'success': False, 'error': 'Insufficient API credits'}

            elif response.status_code != 200:
                return {'success': False, 'error': f'API error: {response.status_code}'}

            # ── Parse result ──────────────────────────────────────────────
            data      = response.json()
            image_b64 = data['artifacts'][0]['base64']

            return {
                'success'  : True,
                'image_b64': image_b64,
                'error'    : None
            }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timed out. Please try again.'}

        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Could not connect to API.'}

        except Exception as e:
            return {'success': False, 'error': f'Error: {str(e)}'}