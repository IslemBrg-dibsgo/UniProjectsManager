# apps.py
"""
University Project Submission Platform - App Configuration

Django app configuration with signal registration.
"""

from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    """
    Configuration for the submissions app.
    
    This class:
    - Sets the app name and verbose name
    - Registers signals when the app is ready
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'submissions'
    verbose_name = 'Project Submissions'
    
    def ready(self):
        """
        Called when the app is ready.
        Import and register signals here.
        """
        # Import signals to register them
        from . import signals  # noqa: F401
