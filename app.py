from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
from datetime import datetime
import requests
import base64
import urllib.parse
import os

app = Flask(__name__)
CORS(app)

# No API keys needed! Pollinations.ai is completely free

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on app startup
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

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Check if user already exists
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 409

        # Insert new user
        hashed_pw = hash_password(password)
        c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                  (name, email, hashed_pw))
        conn.commit()
        conn.close()

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

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        hashed_pw = hash_password(password)
        if user[3] != hashed_pw:
            return jsonify({'error': 'Invalid email or password'}), 401

        token = generate_token()
        
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {'name': user[1], 'email': user[2]}
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

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        # Always return success to prevent email enumeration
        if user:
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
