"""
Email Service for University Project Submission Platform
Handles all email notifications with HTML templates using Mailjet API
"""

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging
import requests

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for sending email notifications via Mailjet API.
    All email methods are designed to be called asynchronously via signals.
    """

    DEFAULT_FROM_EMAIL = getattr(
        settings, 'DEFAULT_FROM_EMAIL', 'noreply@university.edu')
    DEFAULT_FROM_NAME = getattr(
        settings, 'DEFAULT_FROM_NAME', 'University Project Platform')
    SITE_NAME = getattr(settings, 'SITE_NAME', 'University Project Platform')
    SITE_URL = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    # Mailjet API configuration
    MAILJET_API_KEY = getattr(settings, 'MAILJET_API_KEY', None)
    MAILJET_SECRET_KEY = getattr(settings, 'MAILJET_SECRET_KEY', None)
    MAILJET_API_URL = 'https://api.mailjet.com/v3.1/send'

    @classmethod
    def _validate_mailjet_config(cls) -> bool:
        """
        Validate that Mailjet API credentials are configured.

        Returns:
            bool: True if credentials are present
        """
        if not cls.MAILJET_API_KEY or not cls.MAILJET_SECRET_KEY:
            logger.error("Mailjet API credentials not configured in settings")
            return False
        return True

    @classmethod
    def _send_email(cls, subject: str, to_emails: list, template_name: str, context: dict,
                    from_email: str = None, from_name: str = None) -> bool:
        """
        Internal method to send HTML emails via Mailjet API with plain text fallback.

        Args:
            subject: Email subject line
            to_emails: List of recipient email addresses
            template_name: Name of the template (without extension)
            context: Context dictionary for template rendering
            from_email: Sender email (optional, uses DEFAULT_FROM_EMAIL if not provided)
            from_name: Sender name (optional, uses DEFAULT_FROM_NAME if not provided)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not cls._validate_mailjet_config():
            return False

        try:
            # Add common context
            context.update({
                'site_name': cls.SITE_NAME,
                'site_url': cls.SITE_URL,
            })

            # Render HTML template
            html_content = render_to_string(
                f'emails/{template_name}.html', context)

            # Create plain text version
            text_content = strip_tags(html_content)

            # Prepare sender information
            sender_email = from_email or cls.DEFAULT_FROM_EMAIL
            sender_name = from_name or cls.DEFAULT_FROM_NAME

            # Prepare recipients
            recipients = [{'Email': email} for email in to_emails]

            # Prepare Mailjet API payload
            payload = {
                'Messages': [
                    {
                        'From': {
                            'Email': sender_email,
                            'Name': sender_name
                        },
                        'To': recipients,
                        'Subject': f"[{cls.SITE_NAME}] {subject}",
                        'TextPart': text_content,
                        'HTMLPart': html_content,
                    }
                ]
            }

            # Send request to Mailjet API
            response = requests.post(
                cls.MAILJET_API_URL,
                auth=(cls.MAILJET_API_KEY, cls.MAILJET_SECRET_KEY),
                json=payload,
                timeout=10
            )

            # Check response
            if response.status_code == 200:
                response_data = response.json()
                message_info = response_data.get('Messages', [{}])[0]

                # Log success with message ID for tracking
                if message_info.get('Status') == 'success':
                    message_id = message_info.get(
                        'To', [{}])[0].get('MessageID')
                    logger.info(
                        f"✓ Email sent successfully via Mailjet API\n"
                        f"  To: {to_emails}\n"
                        f"  Subject: {subject}\n"
                        f"  Message ID: {message_id}"
                    )
                    return True
                else:
                    logger.error(
                        f"✗ Mailjet API returned non-success status\n"
                        f"  Response: {response_data}"
                    )
                    return False
            else:
                logger.error(
                    f"✗ Mailjet API request failed\n"
                    f"  Status Code: {response.status_code}\n"
                    f"  Response: {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(
                f"✗ Network error sending email via Mailjet API: {str(e)}")
            return False
        except Exception as e:
            logger.error(
                f"✗ Failed to send email to {to_emails}: {str(e)}", exc_info=True)
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
            'is_url_submission': submission.is_url_submission,
            'is_file_submission': submission.is_file_submission,
            'is_both_submission': submission.is_both_submission,
            'repository_url': submission.repository_url if submission.is_url_submission else None,
            'deployed_url': submission.deployed_url if submission.is_url_submission else None,
            'has_project_file': bool(submission.project_file) if submission.is_file_submission else False,
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
            logger.warning(
                f"No collaborators with email addresses for submission {submission.pk}")
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

    @classmethod
    def send_bulk_emails(cls, recipients: list, subject: str, template_name: str,
                         context: dict, batch_size: int = 50) -> dict:
        """
        Send bulk emails to multiple recipients in batches.
        Useful for announcements to all students in a classroom.

        Args:
            recipients: List of email addresses
            subject: Email subject
            template_name: Template name (without extension)
            context: Context for template rendering
            batch_size: Number of emails per API call (Mailjet allows up to 50)

        Returns:
            dict: Summary of results {'success': count, 'failed': count, 'total': count}
        """
        if not cls._validate_mailjet_config():
            return {'success': 0, 'failed': len(recipients), 'total': len(recipients)}

        results = {'success': 0, 'failed': 0, 'total': len(recipients)}

        # Split recipients into batches
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            success = cls._send_email(
                subject=subject,
                to_emails=batch,
                template_name=template_name,
                context=context
            )

            if success:
                results['success'] += len(batch)
            else:
                results['failed'] += len(batch)

        logger.info(
            f"Bulk email completed: {results['success']}/{results['total']} sent successfully"
        )

        return results

    @classmethod
    def test_connection(cls) -> bool:
        """
        Test Mailjet API connection with a simple request.
        Useful for debugging and setup verification.

        Returns:
            bool: True if connection successful
        """
        if not cls._validate_mailjet_config():
            return False

        try:
            # Simple API call to verify credentials
            response = requests.get(
                'https://api.mailjet.com/v3/REST/contact',
                auth=(cls.MAILJET_API_KEY, cls.MAILJET_SECRET_KEY),
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✓ Mailjet API connection successful")
                return True
            else:
                logger.error(
                    f"✗ Mailjet API connection failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ Failed to connect to Mailjet API: {str(e)}")
            return False
