# FoodCam - Food Calorie Estimation Camera

FoodCam is a modern web application that allows users to upload food photos and receive AI-powered predictions for food type, estimated calorie count, and nutritional breakdown.

The project uses computer vision and language models to automate calorie estimation from food images with a clean, organized codebase.

---

## ✨ Features

- 📸 Upload food photos via a modern web interface
- 🤖 Automatic food type classification using PyTorch MobileNetV2 model
- 🔢 Calorie estimation and nutritional analysis using Google's Gemini AI
- 📊 Area detection of food item vs. total image area (OpenCV contour detection)
- 📝 History system for logged-in users and guests
- 🔒 JWT-based authentication with secure user management
- 🚀 RESTful API with comprehensive documentation
- 📱 Responsive Vue.js frontend
- 🛡️ Environment-specific configurations for development/production

---

## 🏗️ Technologies Used

**Backend:**
- Python 3.12
- Django 5.2 with Django REST Framework
- PyTorch for ML model inference
- OpenCV for image processing
- Google Gemini API for nutritional analysis
- MySQL database
- JWT authentication

**Frontend:**
- Vue.js 3 with Vite
- Modern responsive design
- API integration

**DevOps:**
- Environment-specific settings
- Modular project structure
- Docker support (planned)

---

## 📁 Project Structure

```
foodcam/
├── backend/                 # Django backend
│   ├── config/             # Project configuration
│   ├── apps/               # Django applications
│   ├── ml_models/          # ML models and logic
│   ├── requirements/       # Environment-specific requirements
│   └── manage.py
├── frontend/               # Vue.js frontend
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd foodcam
   ```

2. **Backend setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements/development.txt
   cp .env.example .env  # Configure your environment
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

For detailed setup instructions, see [docs/development.md](docs/development.md)

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
