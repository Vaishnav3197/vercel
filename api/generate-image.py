from http.server import BaseHTTPRequestHandler
import json
import requests
import base64
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Check for authorization token
            auth_header = self.headers.get('Authorization')
            if not auth_header:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No authorization token provided'}).encode())
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            prompt = data.get('prompt', '')

            if not prompt:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Prompt is required'}).encode())
                return

            print(f"Generating image for prompt: {prompt}")

            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(prompt)

            # Pollinations.ai API endpoint - no authentication needed!
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

            # Add parameters for better quality
            params = {
                'width': 1024,
                'height': 1024,
                'seed': -1,  # Random seed each time
                'nologo': 'true'
            }

            # Build full URL with parameters
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{image_url}?{param_string}"

            print(f"Requesting image from: {full_url}")

            # Fetch the image
            response = requests.get(full_url, timeout=30)

            if response.status_code == 200:
                # Convert image bytes to base64
                image_bytes = response.content
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                print("Image generated successfully!")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'image': f'data:image/jpeg;base64,{image_base64}',
                    'prompt': prompt
                }).encode())
            else:
                print(f"Error response: {response.status_code}")
                self.send_response(response.status_code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Image generation failed',
                    'details': f'Status code: {response.status_code}'
                }).encode())

        except requests.exceptions.Timeout:
            self.send_response(504)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Request timeout',
                'details': 'Image generation took too long. Please try again.'
            }).encode())
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Image generation error',
                'details': str(e)
            }).encode())
