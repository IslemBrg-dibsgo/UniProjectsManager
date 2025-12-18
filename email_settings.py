# email_settings.py
"""
University Project Submission Platform - Email Configuration

Add these settings to your Django settings.py file to configure email notifications.

This file provides example configurations for different email backends:
1. Console backend (development)
2. SMTP backend (production)
3. Gmail SMTP
4. SendGrid
5. Amazon SES
"""

# =============================================================================
# Development Settings (Console Backend)
# =============================================================================
# Use this for local development - emails will be printed to console

DEVELOPMENT_EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
    'DEFAULT_FROM_EMAIL': 'noreply@university-submissions.local',
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'SITE_URL': 'http://localhost:8000',
}


# =============================================================================
# File Backend (Development/Testing)
# =============================================================================
# Emails are saved to files in the specified directory

FILE_EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.filebased.EmailBackend',
    'EMAIL_FILE_PATH': '/tmp/app-emails',  # Change this path as needed
    'DEFAULT_FROM_EMAIL': 'noreply@university-submissions.local',
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'SITE_URL': 'http://localhost:8000',
}


# =============================================================================
# SMTP Backend (Production)
# =============================================================================
# Generic SMTP configuration

SMTP_EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.your-email-provider.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_USE_SSL': False,
    'EMAIL_HOST_USER': 'your-email@example.com',
    'EMAIL_HOST_PASSWORD': 'your-email-password',  # Use environment variable!
    'DEFAULT_FROM_EMAIL': 'University Submissions <noreply@your-domain.com>',
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'SITE_URL': 'https://your-domain.com',
}


# =============================================================================
# Gmail SMTP
# =============================================================================
# Note: You need to enable "Less secure app access" or use App Passwords

GMAIL_EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'your-email@gmail.com',
    'EMAIL_HOST_PASSWORD': 'your-app-password',  # Use App Password, not regular password
    'DEFAULT_FROM_EMAIL': 'University Submissions <your-email@gmail.com>',
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'SITE_URL': 'https://your-domain.com',
}


# =============================================================================
# SendGrid
# =============================================================================
# Using SendGrid's SMTP relay

SENDGRID_EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.sendgrid.net',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'apikey',  # This is literally 'apikey'
    'EMAIL_HOST_PASSWORD': 'your-sendgrid-api-key',  # Your SendGrid API key
    'DEFAULT_FROM_EMAIL': 'University Submissions <noreply@your-domain.com>',
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'SITE_URL': 'https://your-domain.com',
}


# =============================================================================
# Amazon SES
# =============================================================================
# Using Amazon Simple Email Service

AMAZON_SES_EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'email-smtp.us-east-1.amazonaws.com',  # Change region as needed
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'your-ses-smtp-username',
    'EMAIL_HOST_PASSWORD': 'your-ses-smtp-password',
    'DEFAULT_FROM_EMAIL': 'University Submissions <noreply@your-verified-domain.com>',
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'SITE_URL': 'https://your-domain.com',
}


# =============================================================================
# Example settings.py Integration
# =============================================================================
"""
Add the following to your settings.py:

import os

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@university-submissions.com')

# Custom Settings
ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() == 'true'
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# Email timeout (optional)
EMAIL_TIMEOUT = 10
"""


# =============================================================================
# Environment Variables Example (.env file)
# =============================================================================
"""
# .env file example for production

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=University Submissions <noreply@your-domain.com>
ENABLE_EMAIL_NOTIFICATIONS=True
SITE_URL=https://your-domain.com
"""


# =============================================================================
# Testing Email Configuration
# =============================================================================
"""
To test your email configuration, use the Django shell:

python manage.py shell

>>> from submissions.notifications import send_test_email
>>> send_test_email('your-email@example.com')

Or use Django's built-in mail function:

>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test Subject',
...     'Test message body.',
...     'from@example.com',
...     ['to@example.com'],
...     fail_silently=False,
... )
"""
