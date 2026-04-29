# prompts/services.py

import io
import time
import base64
import requests
from django.conf import settings
from PIL import Image


class ImageToImageService:
    """
    Uses Replicate's FLUX Dev model
    Much better quality than Stability AI
    """

    def __init__(self):
        self.api_key = settings.IMAGE_GEN_API_KEY
        self.api_url = settings.IMAGE_GEN_API_URL
        self.model   = settings.IMAGE_GEN_MODEL

    def transform(self, image_file, prompt_text):
        """
        Always uses 100% strength (prompt_strength=1.0)
        Returns base64 of transformed image
        """

        if not self.api_key:
            return {'success': False, 'error': 'API key not configured'}

        try:
            # ── Prepare Image ─────────────────────────────────────────────
            img = Image.open(image_file)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize to max 1024 (maintains aspect ratio)
            img.thumbnail((1024, 1024), Image.LANCZOS)

            # Convert to base64 — Replicate needs data URI
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)
            img_b64  = base64.b64encode(img_bytes.read()).decode('utf-8')
            data_uri = f"data:image/jpeg;base64,{img_b64}"

            # ── Start Prediction ──────────────────────────────────────────
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type' : 'application/json',
                },
                json={
                    'version': 'black-forest-labs/flux-dev:latest',
                    'input'  : {
                        'image'           : data_uri,
                        'prompt'          : prompt_text,
                        'prompt_strength' : 1.0,      # Always 100%
                        'num_inference_steps': 50,
                        'guidance_scale'  : 7.5,
                        'output_format'   : 'jpg',
                        'output_quality'  : 95,
                    }
                },
                timeout=10
            )

            if response.status_code == 401:
                return {'success': False, 'error': 'Invalid API key'}

            if response.status_code != 201:
                return {'success': False, 'error': f'API error: {response.status_code}'}

            prediction = response.json()
            prediction_id = prediction['id']

            # ── Poll for Result ───────────────────────────────────────────
            max_wait  = 60  # 60 seconds max
            poll_url  = f"{self.api_url}/{prediction_id}"
            start     = time.time()

            while time.time() - start < max_wait:
                check_res = requests.get(
                    poll_url,
                    headers={'Authorization': f'Bearer {self.api_key}'}
                )

                if check_res.status_code != 200:
                    return {'success': False, 'error': 'Polling failed'}

                status_data = check_res.json()
                status_val  = status_data.get('status')

                if status_val == 'succeeded':
                    # Output is URL to image
                    output_url = status_data['output'][0]

                    # Download image
                    img_res = requests.get(output_url, timeout=30)
                    if img_res.status_code != 200:
                        return {'success': False, 'error': 'Download failed'}

                    # Convert to base64
                    result_b64 = base64.b64encode(img_res.content).decode('utf-8')

                    return {
                        'success'  : True,
                        'image_b64': result_b64,
                        'error'    : None
                    }

                elif status_val == 'failed':
                    error_msg = status_data.get('error', 'Generation failed')
                    return {'success': False, 'error': error_msg}

                # Still processing — wait 2 seconds
                time.sleep(2)

            return {'success': False, 'error': 'Timeout waiting for result'}

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timed out'}

        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Could not connect to API'}

        except Exception as e:
            return {'success': False, 'error': f'Error: {str(e)}'}# prompts/services.py

import io
import time
import base64
import requests
from django.conf import settings
from PIL import Image


class ImageToImageService:
    """
    Uses Replicate's FLUX Dev model
    """

    def __init__(self):
        self.api_key = settings.IMAGE_GEN_API_KEY
        self.api_url = settings.IMAGE_GEN_API_URL

    def transform(self, image_file, prompt_text):
        """
        Always uses 100% strength (prompt_strength=1.0)
        Returns base64 of transformed image
        """

        print(f"🔑 API Key exists: {bool(self.api_key)}")
        print(f"🌐 API URL: {self.api_url}")
        print(f"📝 Prompt: {prompt_text[:50]}...")

        if not self.api_key:
            return {'success': False, 'error': 'API key not configured'}

        try:
            # ── Prepare Image ─────────────────────────────────────────────
            img = Image.open(image_file)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            img.thumbnail((1024, 1024), Image.LANCZOS)

            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)
            img_b64  = base64.b64encode(img_bytes.read()).decode('utf-8')
            data_uri = f"data:image/jpeg;base64,{img_b64}"

            print(f"📷 Image prepared, size: {len(img_b64)} bytes")

            # ── Start Prediction ──────────────────────────────────────────
            payload = {
                'version': 'black-forest-labs/flux-dev',
                'input': {
                    'image'          : data_uri,
                    'prompt'         : prompt_text,
                    'prompt_strength': 1.0,
                    'num_outputs'    : 1,
                }
            }

            print(f"🚀 Calling Replicate API...")

            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Token {self.api_key}',
                    'Content-Type' : 'application/json',
                },
                json=payload,
                timeout=10
            )

            print(f"📡 Response status: {response.status_code}")
            print(f"📄 Response body: {response.text[:500]}")

            if response.status_code == 401:
                return {'success': False, 'error': 'Invalid API key'}

            if response.status_code != 201:
                return {
                    'success': False,
                    'error': f'API error {response.status_code}: {response.text[:200]}'
                }

            prediction = response.json()
            prediction_id = prediction.get('id')

            if not prediction_id:
                return {'success': False, 'error': 'No prediction ID returned'}

            print(f"✅ Prediction started: {prediction_id}")

            # ── Poll for Result ───────────────────────────────────────────
            max_wait = 60
            poll_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            start    = time.time()

            while time.time() - start < max_wait:
                print(f"⏳ Polling... ({int(time.time() - start)}s)")

                check_res = requests.get(
                    poll_url,
                    headers={'Authorization': f'Token {self.api_key}'}
                )

                if check_res.status_code != 200:
                    print(f"❌ Poll failed: {check_res.status_code}")
                    return {'success': False, 'error': 'Polling failed'}

                status_data = check_res.json()
                status_val  = status_data.get('status')

                print(f"📊 Status: {status_val}")

                if status_val == 'succeeded':
                    output = status_data.get('output')

                    if not output:
                        return {'success': False, 'error': 'No output in response'}

                    # Output is URL to image
                    output_url = output[0] if isinstance(output, list) else output

                    print(f"🖼️ Downloading from: {output_url}")

                    # Download image
                    img_res = requests.get(output_url, timeout=30)
                    if img_res.status_code != 200:
                        return {'success': False, 'error': 'Download failed'}

                    # Convert to base64
                    result_b64 = base64.b64encode(img_res.content).decode('utf-8')

                    print(f"✅ Success! Image size: {len(result_b64)} bytes")

                    return {
                        'success'  : True,
                        'image_b64': result_b64,
                        'error'    : None
                    }

                elif status_val == 'failed':
                    error_msg = status_data.get('error', 'Generation failed')
                    print(f"❌ Failed: {error_msg}")
                    return {'success': False, 'error': error_msg}

                # Still processing
                time.sleep(2)

            print(f"⏰ Timeout after {max_wait}s")
            return {'success': False, 'error': 'Timeout waiting for result'}

        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout")
            return {'success': False, 'error': 'Request timed out'}

        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Connection error: {e}")
            return {'success': False, 'error': 'Could not connect to API'}

        except Exception as e:
            print(f"💥 Exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'Error: {str(e)}'}