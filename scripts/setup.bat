@echo off
setlocal enabledelayedexpansion

echo 🍕 Setting up FoodCam development environment...

REM Store the root directory
set "ROOT_DIR=%~dp0.."
cd "%ROOT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.12+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

REM Backend setup
echo 🔧 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo 📥 Installing Python dependencies...
if not exist "requirements\development.txt" (
    echo ❌ Error: requirements\development.txt not found!
    pause
    exit /b 1
)

REM Install base requirements first
echo 📥 Installing base requirements...
pip install -r requirements\base.txt
if errorlevel 1 (
    echo ❌ Error installing base requirements!
    pause
    exit /b 1
)

REM Install development requirements
echo 📥 Installing development requirements...
pip install -r requirements\development.txt
if errorlevel 1 (
    echo ❌ Error installing development requirements!
    pause
    exit /b 1
)

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating environment file...
    if exist ".env.example" (
        copy .env.example .env
        echo ⚠️  Please edit .env file with your database credentials and API keys
    ) else (
        echo ❌ Error: .env.example not found!
        pause
        exit /b 1
    )
)

REM Run migrations
echo 🗄️  Running database migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo ❌ Error creating migrations!
    pause
    exit /b 1
)

python manage.py migrate
if errorlevel 1 (
    echo ❌ Error applying migrations!
    pause
    exit /b 1
)

REM Create superuser (optional)
set /p create_superuser="👤 Would you like to create a superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

cd ..

REM Frontend setup
echo 🎨 Setting up frontend...
cd frontend

REM Install Node.js dependencies
echo 📥 Installing Node.js dependencies...
if exist "package.json" (
    npm install
    if errorlevel 1 (
        echo ❌ Error installing Node.js dependencies!
        pause
        exit /b 1
    )
) else (
    echo ❌ Error: package.json not found!
    pause
    exit /b 1
)

cd ..

echo ✅ Setup complete!
echo.
echo 🚀 To start development:
echo    Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python manage.py runserver
echo    Frontend: cd frontend ^&^& npm run dev
echo.
echo 🌐 Access points:
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo    Admin:    http://localhost:8000/admin

pause 