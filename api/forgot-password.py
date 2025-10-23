from http.server import BaseHTTPRequestHandler
import json
import os

# Use Vercel KV (Redis-compatible)
import redis

redis_client = redis.from_url(os.environ.get('KV_URL') or os.environ.get('REDIS_URL', 'redis://localhost:6379'))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            email = data.get('email')

            if not email:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email is required'}).encode())
                return

            # Check if user exists in Redis
            user_exists = redis_client.exists(f"user:{email}")

            # Always return success to prevent email enumeration
            if user_exists:
                # In production, send actual email here
                print(f"Password reset link would be sent to: {email}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'message': 'If an account exists with this email, a password reset link has been sent.'
                }).encode())
            else:
                # Return same message for security
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'message': 'If an account exists with this email, a password reset link has been sent.'
                }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
