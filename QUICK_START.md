# Quick Start Guide

## Fast Setup (Windows)

1. **Run the setup script:**
   ```bash
   setup.bat
   ```

2. **Create your admin account:**
   ```bash
   venv\Scripts\activate
   python manage.py createsuperuser
   ```

3. **Start the server:**
   ```bash
   python manage.py runserver
   ```

4. **Open your browser:**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Fast Setup (macOS/Linux)

1. **Make the script executable and run it:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Create your admin account:**
   ```bash
   source venv/bin/activate
   python manage.py createsuperuser
   ```

3. **Start the server:**
   ```bash
   python manage.py runserver
   ```

4. **Open your browser:**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Manual Setup

If the automatic setup doesn't work:

### 1. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create superuser
```bash
python manage.py createsuperuser
```

### 5. Collect static files
```bash
python manage.py collectstatic
```

### 6. Run server
```bash
python manage.py runserver
```

## First Time Usage

### Register Users

1. Go to http://localhost:8000/auth/register/
2. Create a teacher account (check "Register as Teacher")
3. Create a student account (leave unchecked)

### As Teacher

1. Login at http://localhost:8000/auth/login/
2. Click "Create Classroom" from dashboard
3. Fill in project details
4. Copy the generated join code
5. Share join code with students

### As Student

1. Login at http://localhost:8000/auth/login/
2. Click "Join Classroom" from dashboard
3. Enter the join code from your teacher
4. Submit your project with repository URL
5. Add team members as collaborators

## Common Commands

```bash
# Activate virtual environment (run this first!)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run on different port
python manage.py runserver 8080

# Run tests
python manage.py test

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

## Troubleshooting

### "No module named django"
Make sure you activated the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Database errors
Reset the database:
```bash
# Delete db.sqlite3 file (Windows)
del db.sqlite3

# Delete db.sqlite3 file (macOS/Linux)
rm db.sqlite3

# Recreate database
python manage.py migrate
python manage.py createsuperuser
```

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Port already in use
```bash
# Use a different port
python manage.py runserver 8080
```

## Project Structure

```
UniProjectsManager/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── db.sqlite3            # SQLite database (created after migration)
│
├── uniprojects/          # Project configuration
│   ├── settings.py       # All Django settings
│   └── urls.py           # Root URL routing
│
├── submissions/          # Main app
│   ├── models.py         # Database models
│   ├── views.py          # Class-based views
│   ├── forms.py          # Django forms
│   ├── urls.py           # URL patterns
│   └── templates/        # HTML templates
│
├── static/               # CSS, JavaScript
└── media/                # User uploads
```

## Need Help?

- Read the full [README.md](README.md)
- Check Django docs: https://docs.djangoproject.com/
- Review code comments in the source files

---

**Ready to code!** 🚀

