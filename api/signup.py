from http.server import BaseHTTPRequestHandler
import json
import hashlib
import os
from upstash_redis import Redis
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize Redis client
redis_client = Redis(
    url=os.environ.get('UPSTASH_REDIS_REST_URL'),
    token=os.environ.get('UPSTASH_REDIS_REST_TOKEN')
)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not name or not email or not password:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'All fields are required'}).encode())
                return

            if len(password) < 6:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Password must be at least 6 characters'}).encode())
                return

            # Check if user already exists in Redis
            if redis_client.exists(f"user:{email}"):
                self.send_response(409)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email already registered'}).encode())
                return

            # Create new user in Redis
            hashed_pw = hash_password(password)
            user_data = {
                'name': name,
                'email': email,
                'password': hashed_pw,
                'created_at': datetime.now().isoformat()
            }
            redis_client.set(f"user:{email}", json.dumps(user_data))

            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'message': 'Account created successfully!',
                'user': {'name': name, 'email': email}
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
