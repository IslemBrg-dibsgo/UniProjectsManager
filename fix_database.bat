@echo off
REM Fix database migration issue

echo ===============================================
echo Fixing Database Migration Issue
echo ===============================================
echo.
echo IMPORTANT: Make sure your Django server is STOPPED
echo Press Ctrl+C in the terminal running the server
echo.
pause

echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/4] Deleting old database...
del /F db.sqlite3 2>nul
if exist db.sqlite3 (
    echo ERROR: Could not delete db.sqlite3 - server may still be running
    echo Please stop the Django server and try again
    pause
    exit /b 1
)

echo [3/4] Running migrations...
python manage.py migrate

echo [4/4] Creating admin user...
echo.
echo Now you need to create a superuser account:
python manage.py createsuperuser

echo.
echo ===============================================
echo Database setup complete!
echo ===============================================
echo.
echo You can now start the server:
echo    python manage.py runserver
echo.
pause

