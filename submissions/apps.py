from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'submissions'
    verbose_name = 'University Project Submissions'
    
    def ready(self):
        """Import signals when the app is ready"""
        import submissions.signals

