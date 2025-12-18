# templatetags/submission_tags.py
"""
Custom template tags and filters for the submission platform.

Usage in templates:
    {% load submission_tags %}
    
    {% if user|is_teacher %}
        ...
    {% endif %}
    
    {{ submission.grade|grade_display }}
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# =============================================================================
# Filters for User Role Checking
# =============================================================================

@register.filter
def is_teacher(user):
    """
    Check if user is a teacher.
    
    Usage:
        {% if user|is_teacher %}
            <a href="{% url 'classroom_create' %}">Create Classroom</a>
        {% endif %}
    """
    return hasattr(user, 'teacher_profile')


@register.filter
def is_student(user):
    """
    Check if user is a student (not a teacher).
    
    Usage:
        {% if user|is_student %}
            <a href="{% url 'classroom_join' %}">Join Classroom</a>
        {% endif %}
    """
    return not hasattr(user, 'teacher_profile')


# =============================================================================
# Filters for Grade Display
# =============================================================================

@register.filter
def grade_display(grade):
    """
    Display grade in format X/20.
    
    Usage:
        {{ submission.grade|grade_display }}
    """
    if grade is not None:
        return f"{grade}/20"
    return "Not graded"


@register.filter
def grade_color(grade):
    """
    Return Bootstrap color class based on grade.
    
    Usage:
        <span class="badge bg-{{ submission.grade|grade_color }}">
            {{ submission.grade|grade_display }}
        </span>
    """
    if grade is None:
        return "secondary"
    if grade >= 16:
        return "success"
    if grade >= 12:
        return "primary"
    if grade >= 10:
        return "warning"
    return "danger"


@register.filter
def grade_percentage(grade):
    """
    Convert grade to percentage.
    
    Usage:
        <div class="progress-bar" style="width: {{ submission.grade|grade_percentage }}%">
    """
    if grade is None:
        return 0
    return (grade / 20) * 100


# =============================================================================
# Filters for Status Display
# =============================================================================

@register.filter
def status_badge(status):
    """
    Return Bootstrap badge HTML for status.
    
    Usage:
        {{ submission.status|status_badge }}
    """
    badges = {
        'DRAFT': '<span class="badge bg-secondary">Draft</span>',
        'SUBMITTED': '<span class="badge bg-primary">Submitted</span>',
    }
    return mark_safe(badges.get(status, status))


@register.filter
def status_color(status):
    """
    Return Bootstrap color class for status.
    
    Usage:
        <span class="badge bg-{{ submission.status|status_color }}">
    """
    colors = {
        'DRAFT': 'secondary',
        'SUBMITTED': 'primary',
    }
    return colors.get(status, 'secondary')


# =============================================================================
# Filters for Submission Permissions
# =============================================================================

@register.filter
def can_view(submission, user):
    """
    Check if user can view the submission.
    
    Usage:
        {% if submission|can_view:user %}
            <a href="{% url 'submission_detail' submission.pk %}">View</a>
        {% endif %}
    """
    return submission.can_user_view(user)


@register.filter
def can_edit(submission, user):
    """
    Check if user can edit the submission.
    
    Usage:
        {% if submission|can_edit:user %}
            <a href="{% url 'submission_update' submission.pk %}">Edit</a>
        {% endif %}
    """
    return submission.can_user_edit(user)


# =============================================================================
# Filters for Classroom Permissions
# =============================================================================

@register.filter
def is_classroom_teacher(classroom, user):
    """
    Check if user is the teacher of the classroom.
    
    Usage:
        {% if classroom|is_classroom_teacher:user %}
            <a href="{% url 'classroom_update' classroom.pk %}">Edit</a>
        {% endif %}
    """
    return classroom.teacher == user


@register.filter
def is_classroom_member(classroom, user):
    """
    Check if user is a member of the classroom.
    
    Usage:
        {% if classroom|is_classroom_member:user %}
            <a href="{% url 'submission_create' classroom.pk %}">Submit Project</a>
        {% endif %}
    """
    from ..models import ClassroomMembership
    return ClassroomMembership.objects.filter(
        classroom=classroom,
        student=user
    ).exists()


# =============================================================================
# Simple Tags
# =============================================================================

@register.simple_tag
def get_user_submission(classroom, user):
    """
    Get user's submission in a classroom.
    
    Usage:
        {% get_user_submission classroom user as my_submission %}
        {% if my_submission %}
            ...
        {% endif %}
    """
    from ..models import ProjectSubmission
    return ProjectSubmission.objects.filter(
        classroom=classroom,
        created_by=user
    ).first()


@register.simple_tag
def get_classroom_stats(classroom):
    """
    Get statistics for a classroom.
    
    Usage:
        {% get_classroom_stats classroom as stats %}
        <p>Students: {{ stats.student_count }}</p>
        <p>Submissions: {{ stats.submission_count }}</p>
    """
    from ..models import ProjectSubmission
    
    submissions = ProjectSubmission.objects.filter(classroom=classroom)
    
    return {
        'student_count': classroom.get_student_count(),
        'submission_count': submissions.count(),
        'draft_count': submissions.filter(status='DRAFT').count(),
        'submitted_count': submissions.filter(status='SUBMITTED').count(),
        'graded_count': submissions.filter(grade__isnull=False).count(),
        'pending_count': submissions.filter(status='SUBMITTED', grade__isnull=True).count(),
    }


# =============================================================================
# Inclusion Tags
# =============================================================================

@register.inclusion_tag('submissions/includes/submission_card.html')
def submission_card(submission, user):
    """
    Render a submission card.
    
    Usage:
        {% submission_card submission user %}
    """
    return {
        'submission': submission,
        'user': user,
        'can_view': submission.can_user_view(user),
        'can_edit': submission.can_user_edit(user),
        'is_creator': submission.created_by == user,
    }


@register.inclusion_tag('classrooms/includes/classroom_card.html')
def classroom_card(classroom, user):
    """
    Render a classroom card.
    
    Usage:
        {% classroom_card classroom user %}
    """
    return {
        'classroom': classroom,
        'user': user,
        'is_teacher': classroom.teacher == user,
        'student_count': classroom.get_student_count(),
        'submission_count': classroom.get_submission_count(),
    }


# =============================================================================
# Utility Filters
# =============================================================================

@register.filter
def truncate_url(url, length=50):
    """
    Truncate a URL for display.
    
    Usage:
        {{ submission.repository_url|truncate_url:40 }}
    """
    if len(url) <= length:
        return url
    return url[:length-3] + '...'


@register.filter
def full_name(user):
    """
    Get user's full name or username.
    
    Usage:
        {{ submission.created_by|full_name }}
    """
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.username


@register.filter
def initials(user):
    """
    Get user's initials.
    
    Usage:
        <div class="avatar">{{ user|initials }}</div>
    """
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    return user.username[:2].upper()
