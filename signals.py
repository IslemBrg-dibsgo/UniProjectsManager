# signals.py
"""
University Project Submission Platform - Django Signals

Signals for handling model events, maintaining data integrity,
and triggering email notifications.
"""

from django.db.models.signals import post_save, pre_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

from .models import (
    ProjectSubmission,
    ClassroomMembership
)

logger = logging.getLogger(__name__)


# =============================================================================
# ProjectSubmission Signals
# =============================================================================

@receiver(m2m_changed, sender=ProjectSubmission.collaborators.through)
def validate_collaborators(sender, instance, action, pk_set, **kwargs):
    """
    Validate that collaborators are members of the same classroom.
    
    This signal fires when collaborators are added to a submission.
    It ensures that only students who are members of the classroom
    can be added as collaborators.
    """
    if action in ['pre_add', 'pre_set']:
        if not pk_set:
            return
        
        classroom = instance.classroom
        
        # Get all member IDs for this classroom
        member_ids = set(
            ClassroomMembership.objects.filter(
                classroom=classroom
            ).values_list('student_id', flat=True)
        )
        
        # Check if all collaborators are members
        invalid_collaborators = pk_set - member_ids
        
        if invalid_collaborators:
            raise ValidationError(
                "All collaborators must be members of the same classroom."
            )


@receiver(pre_delete, sender=ClassroomMembership)
def prevent_membership_deletion_with_submission(sender, instance, **kwargs):
    """
    Prevent deletion of membership if student has a submission.
    
    This ensures that students cannot leave a classroom if they
    have created a project submission in it.
    """
    has_submission = ProjectSubmission.objects.filter(
        classroom=instance.classroom,
        created_by=instance.student
    ).exists()
    
    if has_submission:
        raise ValidationError(
            "Cannot remove membership: student has a project submission in this classroom."
        )


# =============================================================================
# Email Notification Signals
# =============================================================================

# Track previous state for detecting changes
_submission_previous_state = {}


@receiver(pre_save, sender=ProjectSubmission)
def store_previous_submission_state(sender, instance, **kwargs):
    """
    Store the previous state of a submission before saving.
    Used to detect status and grade changes for notifications.
    """
    if instance.pk:
        try:
            previous = ProjectSubmission.objects.get(pk=instance.pk)
            _submission_previous_state[instance.pk] = {
                'status': previous.status,
                'grade': previous.grade,
            }
        except ProjectSubmission.DoesNotExist:
            pass


@receiver(post_save, sender=ProjectSubmission)
def notify_on_submission(sender, instance, created, **kwargs):
    """
    Send notification when a project is submitted.
    
    Triggers email to teacher when status changes to SUBMITTED.
    """
    # Check if notifications are enabled
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    # Get previous state
    previous = _submission_previous_state.pop(instance.pk, None)
    
    # Check if status changed to SUBMITTED
    status_changed_to_submitted = (
        previous is not None and
        previous['status'] != 'SUBMITTED' and
        instance.status == 'SUBMITTED'
    )
    
    if status_changed_to_submitted:
        try:
            from .notifications import send_submission_notification
            send_submission_notification(instance)
            logger.info(f"Submission notification triggered for submission {instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send submission notification: {str(e)}")


@receiver(post_save, sender=ProjectSubmission)
def notify_on_grade(sender, instance, created, **kwargs):
    """
    Send notification when a project is graded.
    
    Triggers email to student and collaborators when grade is assigned.
    """
    # Check if notifications are enabled
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    # Skip if this is a new submission (can't be graded yet)
    if created:
        return
    
    # Get previous state (may have been popped by notify_on_submission)
    previous = _submission_previous_state.pop(instance.pk, None)
    
    # If we don't have previous state, try to detect grade change differently
    # This handles the case where grade is being set for the first time
    grade_was_assigned = (
        instance.grade is not None and
        (previous is None or previous.get('grade') is None or previous.get('grade') != instance.grade)
    )
    
    # Only send if grade was just assigned or changed
    if grade_was_assigned and instance.status == 'SUBMITTED':
        try:
            from .notifications import send_grade_notification
            send_grade_notification(instance)
            logger.info(f"Grade notification triggered for submission {instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send grade notification: {str(e)}")


@receiver(post_save, sender=ClassroomMembership)
def notify_on_classroom_join(sender, instance, created, **kwargs):
    """
    Send welcome email when a student joins a classroom.
    
    Triggers email with classroom details when membership is created.
    """
    # Check if notifications are enabled
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    # Only send for new memberships
    if not created:
        return
    
    try:
        from .notifications import send_welcome_email
        send_welcome_email(instance)
        logger.info(f"Welcome email triggered for membership {instance.pk}")
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")


# =============================================================================
# Signal Registration Helper
# =============================================================================

def register_signals():
    """
    Helper function to ensure signals are registered.
    Call this in apps.py ready() method.
    
    Note: Signals are registered via decorators above, so this function
    is primarily for documentation and explicit registration if needed.
    """
    pass  # Signals are registered via decorators above
