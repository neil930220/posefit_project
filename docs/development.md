# Development Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- Git

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

5. **Database setup:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

## Project Structure

The project follows a modular structure:

- `backend/config/` - Django project configuration
- `backend/apps/` - Django applications
- `backend/ml_models/` - Machine learning models and logic
- `frontend/src/` - Vue.js frontend source code

## Environment Settings

The project uses environment-specific settings:

- `config.settings.development` - Development settings
- `config.settings.production` - Production settings
- `config.settings.testing` - Testing settings

## Running Tests

```bash
cd backend
python manage.py test
```

## Code Quality

Run code formatting and linting:

```bash
black .
flake8 .
isort .
``` 