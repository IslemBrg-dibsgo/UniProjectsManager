@echo off
REM Setup script for University Project Submission Platform (Windows)

echo ===============================================
echo University Project Submission Platform Setup
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Running database migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo [5/6] Collecting static files...
python manage.py collectstatic --noinput

echo [6/6] Setup complete!
echo.
echo ===============================================
echo Next steps:
echo ===============================================
echo 1. Create a superuser account:
echo    python manage.py createsuperuser
echo.
echo 2. Start the development server:
echo    python manage.py runserver
echo.
echo 3. Access the application:
echo    Main site: http://localhost:8000
echo    Admin panel: http://localhost:8000/admin
echo.
echo To activate the virtual environment in future:
echo    venv\Scripts\activate
echo ===============================================
echo.
pause

