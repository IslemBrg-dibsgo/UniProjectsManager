#!/bin/bash
# Setup script for University Project Submission Platform (macOS/Linux)

set -e

echo "==============================================="
echo "University Project Submission Platform Setup"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
python3 -m venv venv

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/6] Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "[5/6] Collecting static files..."
python manage.py collectstatic --noinput

echo "[6/6] Setup complete!"
echo ""
echo "==============================================="
echo "Next steps:"
echo "==============================================="
echo "1. Create a superuser account:"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Access the application:"
echo "   Main site: http://localhost:8000"
echo "   Admin panel: http://localhost:8000/admin"
echo ""
echo "To activate the virtual environment in future:"
echo "   source venv/bin/activate"
echo "==============================================="
echo ""

