from http.server import BaseHTTPRequestHandler
import json
import hashlib
import secrets
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_hex(32)

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
            password = data.get('password')

            if not email or not password:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email and password required'}).encode())
                return

            # Get user data from Redis
            user_data = redis_client.get(f"user:{email}")
            if not user_data:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid email or password'}).encode())
                return

            user = json.loads(user_data)
            hashed_pw = hash_password(password)
            if user['password'] != hashed_pw:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid email or password'}).encode())
                return

            token = generate_token()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'message': 'Login successful!',
                'token': token,
                'user': {'name': user['name'], 'email': user['email']}
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
