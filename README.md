# University Project Submission Platform

A comprehensive Django web application for managing university project submissions, built entirely with Django's class-based views. This platform enables teachers to create project assignments (classrooms) and students to submit their projects, with grading and collaboration features.

## Features

### For Teachers
- 📚 **Create and Manage Classrooms** - Create project assignments with descriptions and requirements
- 🔑 **Join Code System** - Each classroom has a unique 8-character join code for students
- 👥 **Student Management** - View enrolled students and manage memberships
- 📊 **Grade Submissions** - Grade student projects with feedback (scale 1-20)
- 📧 **Email Notifications** - Automatic notifications for new submissions
- 📈 **Dashboard** - Overview of classrooms, students, and pending submissions

### For Students
- 🎓 **Join Classrooms** - Join classrooms using teacher-provided join codes
- 📝 **Submit Projects** - Create and submit project assignments
- 👨‍👩‍👧‍👦 **Team Collaboration** - Add collaborators from the same classroom
- 🔗 **Repository Links** - Submit GitHub/GitLab repository and deployment URLs
- ✏️ **Draft Mode** - Save drafts and edit before final submission
- 📬 **Grade Notifications** - Receive email notifications when graded

### Technical Features
- **Class-Based Views** - Built entirely with Django's generic class-based views
- **Custom Permissions** - Role-based access control (Teacher/Student)
- **Signal-Based Notifications** - Django signals trigger email notifications
- **File Uploads** - Upload project requirement documents
- **Advanced Filtering** - Filter submissions by status, grade, classroom, etc.
- **Responsive Design** - Bootstrap 5 for mobile-friendly UI

## Project Structure

```
UniProjectsManager/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
│
├── uniprojects/                 # Main project configuration
│   ├── __init__.py
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
│
├── submissions/                 # Main Django app
│   ├── models.py                # Database models (User, Classroom, Submission)
│   ├── views.py                 # Class-based views
│   ├── forms.py                 # Django forms
│   ├── urls.py                  # App URL patterns
│   ├── admin.py                 # Admin interface customization
│   ├── signals.py               # Email notification signals
│   ├── apps.py                  # App configuration
│   ├── tests.py                 # Unit tests
│   │
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   └── email_service.py     # Email handling service
│   │
│   └── templates/               # HTML templates
│       ├── base.html
│       ├── dashboard_student.html
│       ├── dashboard_teacher.html
│       ├── classrooms/          # Classroom templates
│       ├── submissions/         # Submission templates
│       ├── registration/        # Auth templates
│       └── emails/              # Email templates
│
├── static/                      # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── media/                       # User-uploaded files
    └── classroom_requirements/  # Uploaded requirement documents
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd UniProjectsManager
   ```

2. **Create and activate virtual environment**
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

6. **Collect static files (for production)**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Usage Guide

### First Steps

1. **Register an account** at `/auth/register/`
   - Choose "Register as Teacher" for teacher accounts
   - Leave unchecked for student accounts

2. **Login** at `/auth/login/`

### As a Teacher

1. **Create a classroom** from your dashboard
   - Add title, description, and optional requirements file
   - A unique join code will be generated automatically

2. **Share the join code** with your students

3. **View submissions** when students submit their projects

4. **Grade submissions** with a score (1-20) and feedback

### As a Student

1. **Join a classroom** using the teacher's join code

2. **Create a submission** in the classroom
   - Add project details and repository URL
   - Select team members (collaborators)
   - Save as draft or submit immediately

3. **Submit your project** when ready (converts draft to submitted)

4. **View your grade** and teacher feedback once graded

## Configuration

### Email Settings

By default, emails are printed to the console (development mode).

To configure real email sending, edit `uniprojects/settings.py`:

```python
# For Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@university.edu'
```

### Database

The default configuration uses SQLite. For production, consider PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uniprojects_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Don't forget to install `psycopg2-binary`: `pip install psycopg2-binary`

### Security Settings

Before deploying to production:

1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Update `ALLOWED_HOSTS`
4. Enable HTTPS-only cookies:
   ```python
   CSRF_COOKIE_SECURE = True
   SESSION_COOKIE_SECURE = True
   ```

## Models Overview

### User
- Extended Django `AbstractUser`
- Added `is_teacher` boolean field
- Role-based permissions

### Classroom
- Represents a project assignment
- Has unique join code for enrollment
- Belongs to one teacher
- Can have many student members

### ClassroomMembership
- Links students to classrooms
- Tracks join date

### ProjectSubmission
- Student project submission
- Can have multiple collaborators
- Status: DRAFT or SUBMITTED
- Grade: 1-20 scale
- Includes repository URL and optional deployed URL

## URL Structure

```
/                                  Dashboard (role-aware)
/auth/register/                    User registration
/auth/login/                       User login
/auth/logout/                      User logout

/classrooms/                       List classrooms
/classrooms/create/                Create classroom (teachers)
/classrooms/join/                  Join classroom (students)
/classrooms/<id>/                  Classroom detail
/classrooms/<id>/edit/             Edit classroom
/classrooms/<id>/members/          View members
/classrooms/<id>/submissions/      Classroom submissions (teachers)

/submissions/                      List submissions
/submissions/<id>/                 Submission detail
/submissions/<id>/edit/            Edit submission (draft only)
/submissions/<id>/submit/          Submit project
/submissions/<id>/grade/           Grade submission (teachers)

/admin/                            Django admin panel
```

## Management Commands

Django provides several useful management commands:

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

## Development

### Adding New Features

1. Models: Update `submissions/models.py`
2. Views: Add to `submissions/views.py`
3. URLs: Update `submissions/urls.py`
4. Templates: Add to `submissions/templates/`
5. Run migrations if models changed

### Testing

Run the test suite:
```bash
python manage.py test submissions
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `SECRET_KEY` from environment variable
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Configure production database (PostgreSQL)
- [ ] Set up email backend (SendGrid, AWS SES, etc.)
- [ ] Configure static file serving (WhiteNoise or CDN)
- [ ] Set up media file storage (AWS S3 or similar)
- [ ] Enable HTTPS
- [ ] Configure logging
- [ ] Set up backup strategy

### Deployment Options

**Option 1: Traditional Server**
- Use Gunicorn as WSGI server
- Nginx as reverse proxy
- PostgreSQL database

**Option 2: Platform as a Service**
- Heroku
- PythonAnywhere
- Railway
- Render

**Option 3: Cloud Providers**
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service

## Troubleshooting

### Database Issues
```bash
# Reset database (development only)
python manage.py flush

# Reset migrations (development only)
python manage.py migrate submissions zero
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear
```

### Permission Errors
- Ensure your user has proper `is_teacher` flag set in admin panel
- Check if user is authenticated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is created for educational purposes.

## Support

For issues and questions:
- Check the Django documentation: https://docs.djangoproject.com/
- Review the code comments and docstrings
- Open an issue in the repository

## Acknowledgments

- Built with Django 5.0
- UI powered by Bootstrap 5
- Icons from Bootstrap Icons
- Template architecture inspired by Django best practices

---

**Made with ❤️ using Django Class-Based Views**
