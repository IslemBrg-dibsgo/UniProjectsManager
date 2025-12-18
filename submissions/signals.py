"""
Django Signals for University Project Submission Platform
Triggers email notifications on model changes
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from .models import User, ClassroomMembership, ProjectSubmission
from .services.email_service import EmailService

import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SUBMISSION SIGNALS
# =============================================================================

@receiver(pre_save, sender=ProjectSubmission)
def track_submission_changes(sender, instance, **kwargs):
    """
    Track changes to submission before save.
    Store original values for comparison in post_save.
    """
    if instance.pk:
        try:
            original = ProjectSubmission.objects.get(pk=instance.pk)
            instance._original_status = original.status
            instance._original_grade = original.grade
        except ProjectSubmission.DoesNotExist:
            instance._original_status = None
            instance._original_grade = None
    else:
        instance._original_status = None
        instance._original_grade = None


@receiver(post_save, sender=ProjectSubmission)
def handle_submission_changes(sender, instance, created, **kwargs):
    """
    Handle submission changes and send appropriate notifications.
    
    Triggers:
    - Email to teacher when status changes from DRAFT to SUBMITTED
    - Email to collaborators when grade is assigned or updated
    """
    # Skip if email notifications are disabled
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    original_status = getattr(instance, '_original_status', None)
    original_grade = getattr(instance, '_original_grade', None)
    
    # Check if submission was just submitted (status changed to SUBMITTED)
    if (original_status == ProjectSubmission.Status.DRAFT and 
        instance.status == ProjectSubmission.Status.SUBMITTED):
        
        logger.info(f"Submission {instance.pk} was submitted, sending notification to teacher")
        
        try:
            EmailService.send_submission_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send submission notification: {str(e)}")
    
    # Check if grade was assigned or updated
    if instance.grade is not None and instance.grade != original_grade:
        logger.info(f"Submission {instance.pk} was graded ({instance.grade}/20), sending notification to collaborators")
        
        try:
            EmailService.send_grade_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send grade notification: {str(e)}")


# =============================================================================
# MEMBERSHIP SIGNALS
# =============================================================================

@receiver(post_save, sender=ClassroomMembership)
def handle_classroom_join(sender, instance, created, **kwargs):
    """
    Send notification to teacher when a student joins their classroom.
    
    Only triggers on new membership creation, not updates.
    """
    # Skip if email notifications are disabled
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    if created:
        logger.info(
            f"Student {instance.student.username} joined classroom {instance.classroom.title}, "
            f"sending notification to teacher"
        )
        
        try:
            EmailService.send_classroom_join_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send classroom join notification: {str(e)}")


# =============================================================================
# USER SIGNALS
# =============================================================================

@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    """
    Send welcome email to newly registered users.
    """
    # Skip if email notifications are disabled
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    if created and instance.email:
        logger.info(f"New user registered: {instance.username}, sending welcome email")
        
        try:
            EmailService.send_welcome_email(instance)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")


# =============================================================================
# CUSTOM SIGNALS (for manual triggering)
# =============================================================================

from django.dispatch import Signal

# Signal for sending submission reminders (can be triggered by management command)
submission_reminder = Signal()

@receiver(submission_reminder)
def handle_submission_reminder(sender, submission, **kwargs):
    """
    Handle submission reminder signal.
    Useful for scheduled tasks/cron jobs.
    """
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    if submission.is_draft:
        try:
            EmailService.send_submission_reminder(submission)
        except Exception as e:
            logger.error(f"Failed to send submission reminder: {str(e)}")
