# AI Portal - Authentication & Image Generation

A Flask-based web application that provides user authentication and AI-powered image generation using Pollinations.ai. This project features a modern, responsive frontend with secure backend APIs, all running without any API keys required.

## 🚀 Features

- **User Authentication**: Secure signup, login, and password reset functionality
- **AI Image Generation**: Generate stunning images from text prompts using Pollinations.ai (completely free, no API keys needed!)
- **Responsive Design**: Modern, mobile-friendly UI with smooth animations
- **Database Integration**: SQLite database for user management
- **CORS Support**: Cross-origin resource sharing enabled for development
- **Session Management**: Token-based authentication with session storage
- **Health Check**: Server status monitoring endpoint

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite3
- **AI Service**: Pollinations.ai (free image generation)
- **Deployment**: Heroku-ready (Procfile included)
- **Dependencies**: Flask-CORS, Requests

## 📋 Prerequisites

- Python 3.11.7 or higher
- pip (Python package manager)

## 🔧 Installation

1. **Clone the repository** (if applicable) or download the files to your local machine.

2. **Navigate to the project directory**:
   ```bash
   cd /path/to/your/project
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Access the application**:
   - Sign up for a new account or log in with existing credentials
   - Navigate to the dashboard to generate AI images
   - Enter a text prompt and click "Generate Image"

## 📡 API Endpoints

### Authentication
- `POST /signup` - Create a new user account
- `POST /login` - Authenticate user and return token
- `POST /forgot-password` - Request password reset (placeholder)

### AI Features
- `POST /ai/generate-image` - Generate image from text prompt (requires auth token)

### Utility
- `GET /` - Serve the main HTML page
- `GET /health` - Health check endpoint

## 🗄️ Database

The application uses SQLite3 for user data storage. The database file (`users.db`) is automatically created on first run and includes:
- User information (name, email, hashed password)
- Account creation timestamps

## 🌐 Deployment

This application is configured for Heroku deployment:

- **Procfile**: Defines the web process
- **runtime.txt**: Specifies Python version
- **requirements.txt**: Lists all dependencies

To deploy to Heroku:
1. Create a Heroku app
2. Push your code to Heroku
3. The app will automatically start using the Procfile

## 🔒 Security Features

- Password hashing using SHA-256
- Token-based authentication
- CORS protection
- Input validation
- Secure session management

## 🎨 Usage Examples

### Generating Images
1. Log in to your account
2. Enter a descriptive prompt, e.g.:
   - "A serene mountain landscape at sunset with a lake reflecting golden light"
   - "A futuristic cityscape with flying cars and neon lights"
3. Click "Generate Image" and wait 10-20 seconds
4. View and download your generated image

### API Usage
```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Generate Image (replace TOKEN with actual token)
curl -X POST http://localhost:5000/ai/generate-image \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"prompt":"A beautiful sunset over the ocean"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open-source. Feel free to use and modify as needed.

## 📞 Support

If you encounter any issues or have questions:
- Check the console for error messages
- Ensure all dependencies are installed
- Verify the server is running on the correct port

---

**Note**: This application uses Pollinations.ai for image generation, which is completely free and requires no API keys. All image generation happens server-side to maintain security.
