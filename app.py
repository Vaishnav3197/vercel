from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import redis
import hashlib
import secrets
from datetime import datetime
import requests
import base64
import urllib.parse
import os
import json

app = Flask(__name__)
CORS(app)

# No API keys needed! Pollinations.ai is completely free

# Database setup - Using Upstash Redis for Vercel
def get_redis_client():
    """Get Redis client for data storage"""
    try:
        # Try Upstash Redis first (for production/Vercel)
        redis_url = os.environ.get('UPSTASH_REDIS_REST_URL')
        redis_token = os.environ.get('UPSTASH_REDIS_REST_TOKEN')

        if redis_url and redis_token:
            # Use Upstash REST API for serverless environments
            import upstash_redis
            return upstash_redis.Redis(url=redis_url, token=redis_token), 'upstash'
        else:
            # Fallback to local Redis (for development)
            return redis.Redis(host='localhost', port=6379, decode_responses=True), 'local'
    except Exception:
        # If Redis fails, we'll use in-memory storage (not persistent)
        return None, 'memory'

# Global storage for in-memory fallback
memory_users = {}

def init_db():
    """Initialize database - no setup needed for Redis"""
    pass

# Initialize on startup
init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_hex(32)

@app.route('/')
def home():
    """Serve the index.html file"""
    return send_file('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        redis_client, db_type = get_redis_client()

        # Check if user already exists
        if db_type == 'upstash':
            existing_user = redis_client.get(f"user:{email}")
            if existing_user:
                return jsonify({'error': 'Email already registered'}), 409
        elif db_type == 'local':
            if redis_client.exists(f"user:{email}"):
                return jsonify({'error': 'Email already registered'}), 409
        else:  # memory
            if email in memory_users:
                return jsonify({'error': 'Email already registered'}), 409

        # Create user data
        user_data = {
            'name': name,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat()
        }

        # Store user
        if db_type == 'upstash':
            redis_client.set(f"user:{email}", json.dumps(user_data))
        elif db_type == 'local':
            redis_client.set(f"user:{email}", json.dumps(user_data))
        else:  # memory
            memory_users[email] = user_data

        return jsonify({
            'message': 'Account created successfully!',
            'user': {'name': name, 'email': email}
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        redis_client, db_type = get_redis_client()

        # Get user data
        if db_type == 'upstash':
            user_data = redis_client.get(f"user:{email}")
            if user_data:
                user = json.loads(user_data)
            else:
                user = None
        elif db_type == 'local':
            user_data = redis_client.get(f"user:{email}")
            if user_data:
                user = json.loads(user_data)
            else:
                user = None
        else:  # memory
            user = memory_users.get(email)

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        hashed_pw = hash_password(password)
        if user['password'] != hashed_pw:
            return jsonify({'error': 'Invalid email or password'}), 401

        token = generate_token()

        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {'name': user['name'], 'email': user['email']}
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Handle password reset request"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        redis_client, db_type = get_redis_client()

        # Check if user exists
        if db_type == 'upstash':
            user_data = redis_client.get(f"user:{email}")
            user_exists = user_data is not None
        elif db_type == 'local':
            user_exists = redis_client.exists(f"user:{email}")
        else:  # memory
            user_exists = email in memory_users

        # Always return success to prevent email enumeration
        if user_exists:
            # In production, send actual email here
            print(f"Password reset link would be sent to: {email}")
            return jsonify({
                'message': 'If an account exists with this email, a password reset link has been sent.'
            }), 200
        else:
            # Return same message for security
            return jsonify({
                'message': 'If an account exists with this email, a password reset link has been sent.'
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai/generate-image', methods=['POST'])
def generate_image():
    """
    Generate image using Pollinations.ai - completely free, no API key needed!
    """
    try:
        # Check for authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401

        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

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
            
            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{image_base64}',
                'prompt': prompt
            }), 200
        else:
            print(f"Error response: {response.status_code}")
            return jsonify({
                'error': 'Image generation failed',
                'details': f'Status code: {response.status_code}'
            }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout',
            'details': 'Image generation took too long. Please try again.'
        }), 504
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({
            'error': 'Image generation error',
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'Server is running', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("🚀 Server starting on http://localhost:5000")
    print("📊 Database initialized")
    print("🔐 CORS enabled for local development")
    print("🎨 Image Generation: Pollinations.ai (FREE - No API key needed!)")
    print("=" * 60)
    print("\n✨ NO API KEYS REQUIRED - Just run and use!")
    print("=" * 60)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
