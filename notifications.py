# notifications.py
"""
University Project Submission Platform - Email Notifications

This module handles all email notifications for the platform:
1. Project submission notification to teacher
2. Grade notification to student and collaborators
3. Welcome email when student joins a classroom

Uses Django's built-in email backend with HTML templates.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Email Configuration
# =============================================================================

def get_site_url():
    """Get the site URL from settings or use default"""
    return getattr(settings, 'SITE_URL', 'http://localhost:8000')


def get_from_email():
    """Get the from email address"""
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@university-submissions.com')


# =============================================================================
# Project Submission Notification
# =============================================================================

def send_submission_notification(submission):
    """
    Send email notification to teacher when a student submits their project.
    
    Args:
        submission: ProjectSubmission instance that was just submitted
    
    Returns:
        bool: True if email was sent successfully
    """
    try:
        teacher = submission.classroom.teacher
        student = submission.created_by
        classroom = submission.classroom
        
        # Build context for template
        context = {
            'teacher_name': teacher.first_name or teacher.username,
            'student_name': f"{student.first_name} {student.last_name}".strip() or student.username,
            'student_email': student.email,
            'project_title': submission.title,
            'classroom_title': classroom.title,
            'repository_url': submission.repository_url,
            'deployed_url': submission.deployed_url,
            'submission_url': f"{get_site_url()}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
            'classroom_url': f"{get_site_url()}{reverse('teacher_submission_list', kwargs={'classroom_pk': classroom.pk})}",
            'collaborators': list(submission.collaborators.all()),
            'submitted_at': submission.submitted_at,
            'site_url': get_site_url(),
        }
        
        # Render HTML template
        html_content = render_to_string('emails/submission_notification.html', context)
        text_content = strip_tags(html_content)
        
        # Create email
        subject = f"[{classroom.title}] New Project Submission: {submission.title}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=get_from_email(),
            to=[teacher.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Submission notification sent to {teacher.email} for submission {submission.pk}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send submission notification: {str(e)}")
        return False


# =============================================================================
# Grade Notification
# =============================================================================

def send_grade_notification(submission):
    """
    Send email notification to student and collaborators when project is graded.
    
    Args:
        submission: ProjectSubmission instance that was just graded
    
    Returns:
        bool: True if all emails were sent successfully
    """
    try:
        classroom = submission.classroom
        teacher = classroom.teacher
        
        # Get all recipients (creator + collaborators)
        recipients = [submission.created_by]
        recipients.extend(list(submission.collaborators.all()))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recipients = []
        for r in recipients:
            if r.id not in seen:
                seen.add(r.id)
                unique_recipients.append(r)
        
        success = True
        
        for recipient in unique_recipients:
            try:
                # Build context for template
                context = {
                    'student_name': recipient.first_name or recipient.username,
                    'teacher_name': f"{teacher.first_name} {teacher.last_name}".strip() or teacher.username,
                    'project_title': submission.title,
                    'classroom_title': classroom.title,
                    'grade': submission.grade,
                    'grade_percentage': (submission.grade / 20) * 100,
                    'teacher_notes': submission.teacher_notes,
                    'submission_url': f"{get_site_url()}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
                    'grades_url': f"{get_site_url()}{reverse('my_grades')}",
                    'is_passing': submission.grade >= 10,
                    'grade_description': get_grade_description(submission.grade),
                    'site_url': get_site_url(),
                }
                
                # Render HTML template
                html_content = render_to_string('emails/grade_notification.html', context)
                text_content = strip_tags(html_content)
                
                # Create email
                subject = f"[{classroom.title}] Your Project Has Been Graded: {submission.grade}/20"
                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=get_from_email(),
                    to=[recipient.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)
                
                logger.info(f"Grade notification sent to {recipient.email} for submission {submission.pk}")
                
            except Exception as e:
                logger.error(f"Failed to send grade notification to {recipient.email}: {str(e)}")
                success = False
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to send grade notifications: {str(e)}")
        return False


def get_grade_description(grade):
    """Convert numeric grade to French description"""
    if grade >= 16:
        return 'Très Bien (Excellent)'
    if grade >= 14:
        return 'Bien (Good)'
    if grade >= 12:
        return 'Assez Bien (Fairly Good)'
    if grade >= 10:
        return 'Passable (Pass)'
    return 'Insuffisant (Fail)'


# =============================================================================
# Welcome Email (Classroom Join)
# =============================================================================

def send_welcome_email(membership):
    """
    Send welcome email when a student joins a classroom.
    
    Args:
        membership: ClassroomMembership instance that was just created
    
    Returns:
        bool: True if email was sent successfully
    """
    try:
        student = membership.student
        classroom = membership.classroom
        teacher = classroom.teacher
        
        # Build context for template
        context = {
            'student_name': student.first_name or student.username,
            'classroom_title': classroom.title,
            'classroom_description': classroom.description,
            'classroom_subject': classroom.subject,
            'teacher_name': f"{teacher.first_name} {teacher.last_name}".strip() or teacher.username,
            'teacher_email': teacher.email,
            'join_code': classroom.join_code,
            'has_requirements_file': bool(classroom.requirements_file),
            'classroom_url': f"{get_site_url()}{reverse('classroom_detail', kwargs={'pk': classroom.pk})}",
            'submission_url': f"{get_site_url()}{reverse('submission_create', kwargs={'classroom_pk': classroom.pk})}",
            'joined_at': membership.joined_at,
            'site_url': get_site_url(),
        }
        
        # Render HTML template
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = strip_tags(html_content)
        
        # Create email
        subject = f"Welcome to {classroom.title}!"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=get_from_email(),
            to=[student.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Welcome email sent to {student.email} for classroom {classroom.pk}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return False


# =============================================================================
# Deadline Reminder (Bonus)
# =============================================================================

def send_deadline_reminder(classroom, students, hours_remaining):
    """
    Send deadline reminder to students who haven't submitted.
    
    Args:
        classroom: Classroom instance
        students: List of User instances who haven't submitted
        hours_remaining: Hours until deadline
    
    Returns:
        int: Number of emails sent successfully
    """
    sent_count = 0
    
    for student in students:
        try:
            context = {
                'student_name': student.first_name or student.username,
                'classroom_title': classroom.title,
                'hours_remaining': hours_remaining,
                'classroom_url': f"{get_site_url()}{reverse('classroom_detail', kwargs={'pk': classroom.pk})}",
                'submission_url': f"{get_site_url()}{reverse('submission_create', kwargs={'classroom_pk': classroom.pk})}",
                'site_url': get_site_url(),
            }
            
            html_content = render_to_string('emails/deadline_reminder.html', context)
            text_content = strip_tags(html_content)
            
            subject = f"[Reminder] {classroom.title} - Deadline in {hours_remaining} hours"
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=get_from_email(),
                to=[student.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            sent_count += 1
            logger.info(f"Deadline reminder sent to {student.email}")
            
        except Exception as e:
            logger.error(f"Failed to send deadline reminder to {student.email}: {str(e)}")
    
    return sent_count


# =============================================================================
# Utility Functions
# =============================================================================

def send_test_email(to_email):
    """
    Send a test email to verify email configuration.
    
    Args:
        to_email: Email address to send test to
    
    Returns:
        bool: True if email was sent successfully
    """
    try:
        subject = "Test Email - University Project Submission Platform"
        message = """
        This is a test email from the University Project Submission Platform.
        
        If you received this email, your email configuration is working correctly.
        
        Configuration:
        - EMAIL_BACKEND: {backend}
        - EMAIL_HOST: {host}
        - DEFAULT_FROM_EMAIL: {from_email}
        """.format(
            backend=getattr(settings, 'EMAIL_BACKEND', 'Not configured'),
            host=getattr(settings, 'EMAIL_HOST', 'Not configured'),
            from_email=get_from_email(),
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=get_from_email(),
            recipient_list=[to_email],
            fail_silently=False,
        )
        
        logger.info(f"Test email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
        return False
