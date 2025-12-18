"""
Email Service for University Project Submission Platform
Handles all email notifications with HTML templates
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for sending email notifications.
    All email methods are designed to be called asynchronously via signals.
    """
    
    DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@university.edu')
    SITE_NAME = getattr(settings, 'SITE_NAME', 'University Project Platform')
    SITE_URL = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    @classmethod
    def _send_email(cls, subject: str, to_emails: list, template_name: str, context: dict) -> bool:
        """
        Internal method to send HTML emails with plain text fallback.
        
        Args:
            subject: Email subject line
            to_emails: List of recipient email addresses
            template_name: Name of the template (without extension)
            context: Context dictionary for template rendering
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Add common context
            context.update({
                'site_name': cls.SITE_NAME,
                'site_url': cls.SITE_URL,
            })
            
            # Render HTML template
            html_content = render_to_string(f'emails/{template_name}.html', context)
            
            # Create plain text version
            text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=f"[{cls.SITE_NAME}] {subject}",
                body=text_content,
                from_email=cls.DEFAULT_FROM_EMAIL,
                to=to_emails,
            )
            
            # Attach HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            logger.info(f"Email sent successfully to {to_emails}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}: {str(e)}")
            return False
    
    @classmethod
    def send_submission_notification(cls, submission) -> bool:
        """
        Send notification to teacher when a student submits a project.
        
        Args:
            submission: ProjectSubmission instance that was submitted
            
        Returns:
            bool: True if email sent successfully
        """
        teacher = submission.classroom.teacher
        
        if not teacher.email:
            logger.warning(f"Teacher {teacher.username} has no email address")
            return False
        
        context = {
            'teacher_name': teacher.get_full_name() or teacher.username,
            'student_name': submission.created_by.get_full_name() or submission.created_by.username,
            'project_title': submission.title,
            'classroom_title': submission.classroom.title,
            'submission_url': f"{cls.SITE_URL}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
            'classroom_url': f"{cls.SITE_URL}{reverse('classroom_detail', kwargs={'pk': submission.classroom.pk})}",
            'collaborators': [c.get_full_name() or c.username for c in submission.collaborators.all()],
            'repository_url': submission.repository_url,
            'deployed_url': submission.deployed_url,
            'submitted_at': submission.submitted_at,
        }
        
        return cls._send_email(
            subject=f"New Submission: {submission.title}",
            to_emails=[teacher.email],
            template_name='submission_notification',
            context=context
        )
    
    @classmethod
    def send_grade_notification(cls, submission) -> bool:
        """
        Send notification to all collaborators when a submission is graded.
        
        Args:
            submission: ProjectSubmission instance that was graded
            
        Returns:
            bool: True if all emails sent successfully
        """
        collaborator_emails = [
            c.email for c in submission.collaborators.all() 
            if c.email
        ]
        
        if not collaborator_emails:
            logger.warning(f"No collaborators with email addresses for submission {submission.pk}")
            return False
        
        context = {
            'project_title': submission.title,
            'classroom_title': submission.classroom.title,
            'teacher_name': submission.classroom.teacher.get_full_name() or submission.classroom.teacher.username,
            'grade': submission.grade,
            'max_grade': 20,
            'teacher_notes': submission.teacher_notes,
            'submission_url': f"{cls.SITE_URL}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
            'grade_percentage': (submission.grade / 20) * 100 if submission.grade else 0,
        }
        
        # Determine grade status for styling
        if submission.grade >= 16:
            context['grade_status'] = 'excellent'
            context['grade_message'] = 'Excellent work! Outstanding performance.'
        elif submission.grade >= 14:
            context['grade_status'] = 'good'
            context['grade_message'] = 'Great job! Very good performance.'
        elif submission.grade >= 12:
            context['grade_status'] = 'above_average'
            context['grade_message'] = 'Good work! Above average performance.'
        elif submission.grade >= 10:
            context['grade_status'] = 'average'
            context['grade_message'] = 'Satisfactory. Meets minimum requirements.'
        else:
            context['grade_status'] = 'below_average'
            context['grade_message'] = 'Needs improvement. Please review the feedback.'
        
        return cls._send_email(
            subject=f"Your Project Has Been Graded: {submission.title}",
            to_emails=collaborator_emails,
            template_name='grade_notification',
            context=context
        )
    
    @classmethod
    def send_classroom_join_notification(cls, membership) -> bool:
        """
        Send notification to teacher when a student joins their classroom.
        
        Args:
            membership: ClassroomMembership instance that was created
            
        Returns:
            bool: True if email sent successfully
        """
        teacher = membership.classroom.teacher
        student = membership.student
        
        if not teacher.email:
            logger.warning(f"Teacher {teacher.username} has no email address")
            return False
        
        context = {
            'teacher_name': teacher.get_full_name() or teacher.username,
            'student_name': student.get_full_name() or student.username,
            'student_email': student.email,
            'classroom_title': membership.classroom.title,
            'classroom_url': f"{cls.SITE_URL}{reverse('classroom_detail', kwargs={'pk': membership.classroom.pk})}",
            'members_url': f"{cls.SITE_URL}{reverse('classroom_members', kwargs={'classroom_pk': membership.classroom.pk})}",
            'joined_at': membership.joined_at,
            'total_students': membership.classroom.get_student_count(),
        }
        
        return cls._send_email(
            subject=f"New Student Joined: {membership.classroom.title}",
            to_emails=[teacher.email],
            template_name='classroom_join_notification',
            context=context
        )
    
    @classmethod
    def send_welcome_email(cls, user) -> bool:
        """
        Send welcome email to newly registered users.
        
        Args:
            user: User instance that was created
            
        Returns:
            bool: True if email sent successfully
        """
        if not user.email:
            logger.warning(f"User {user.username} has no email address")
            return False
        
        context = {
            'user_name': user.get_full_name() or user.username,
            'is_teacher': user.is_teacher,
            'login_url': f"{cls.SITE_URL}{reverse('login')}",
            'dashboard_url': f"{cls.SITE_URL}{reverse('dashboard')}",
        }
        
        if user.is_teacher:
            context['create_classroom_url'] = f"{cls.SITE_URL}{reverse('classroom_create')}"
        else:
            context['join_classroom_url'] = f"{cls.SITE_URL}{reverse('classroom_join')}"
        
        return cls._send_email(
            subject="Welcome to University Project Platform",
            to_emails=[user.email],
            template_name='welcome_email',
            context=context
        )
    
    @classmethod
    def send_submission_reminder(cls, submission) -> bool:
        """
        Send reminder to collaborators about a draft submission.
        
        Args:
            submission: ProjectSubmission instance in draft status
            
        Returns:
            bool: True if email sent successfully
        """
        collaborator_emails = [
            c.email for c in submission.collaborators.all() 
            if c.email
        ]
        
        if not collaborator_emails:
            return False
        
        context = {
            'project_title': submission.title,
            'classroom_title': submission.classroom.title,
            'submission_url': f"{cls.SITE_URL}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
            'edit_url': f"{cls.SITE_URL}{reverse('submission_update', kwargs={'pk': submission.pk})}",
            'created_at': submission.created_at,
        }
        
        return cls._send_email(
            subject=f"Reminder: Submit Your Project - {submission.title}",
            to_emails=collaborator_emails,
            template_name='submission_reminder',
            context=context
        )
