# utils.py
"""
University Project Submission Platform - Utility Functions

Helper functions and utilities used across the application.
"""

import re
from django.utils.crypto import get_random_string


# =============================================================================
# Join Code Generation
# =============================================================================

def generate_join_code(length=8):
    """
    Generate a unique join code for classrooms.
    
    Uses uppercase letters and numbers, excluding ambiguous characters
    (0, O, 1, I, L) for better readability.
    
    Args:
        length: Length of the code (default: 8)
    
    Returns:
        str: A random join code
    """
    # Exclude ambiguous characters: 0, O, 1, I, L
    allowed_chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    return get_random_string(length, allowed_chars=allowed_chars)


def is_valid_join_code(code):
    """
    Validate a join code format.
    
    Args:
        code: The code to validate
    
    Returns:
        bool: True if valid format
    """
    if not code or len(code) != 8:
        return False
    return bool(re.match(r'^[A-Z0-9]{8}$', code.upper()))


# =============================================================================
# URL Validation
# =============================================================================

def is_valid_github_url(url):
    """
    Check if URL is a valid GitHub repository URL.
    
    Args:
        url: The URL to validate
    
    Returns:
        bool: True if valid GitHub URL
    """
    patterns = [
        r'^https?://github\.com/[\w-]+/[\w.-]+/?$',
        r'^https?://github\.com/[\w-]+/[\w.-]+\.git$',
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def is_valid_gitlab_url(url):
    """
    Check if URL is a valid GitLab repository URL.
    
    Args:
        url: The URL to validate
    
    Returns:
        bool: True if valid GitLab URL
    """
    patterns = [
        r'^https?://gitlab\.com/[\w-]+/[\w.-]+/?$',
        r'^https?://gitlab\.com/[\w-]+/[\w.-]+\.git$',
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def is_valid_repository_url(url):
    """
    Check if URL is a valid repository URL (GitHub or GitLab).
    
    Args:
        url: The URL to validate
    
    Returns:
        bool: True if valid repository URL
    """
    return is_valid_github_url(url) or is_valid_gitlab_url(url)


def extract_repo_name(url):
    """
    Extract repository name from a GitHub/GitLab URL.
    
    Args:
        url: The repository URL
    
    Returns:
        str: Repository name or None
    """
    match = re.search(r'github\.com/[\w-]+/([\w.-]+)', url)
    if match:
        return match.group(1).replace('.git', '')
    
    match = re.search(r'gitlab\.com/[\w-]+/([\w.-]+)', url)
    if match:
        return match.group(1).replace('.git', '')
    
    return None


# =============================================================================
# Grade Calculations
# =============================================================================

def calculate_grade_statistics(grades):
    """
    Calculate statistics for a list of grades.
    
    Args:
        grades: List of grade values (integers 1-20)
    
    Returns:
        dict: Statistics including average, min, max, median
    """
    if not grades:
        return {
            'count': 0,
            'average': None,
            'min': None,
            'max': None,
            'median': None,
            'passing_count': 0,
            'passing_rate': 0,
        }
    
    grades = [g for g in grades if g is not None]
    
    if not grades:
        return {
            'count': 0,
            'average': None,
            'min': None,
            'max': None,
            'median': None,
            'passing_count': 0,
            'passing_rate': 0,
        }
    
    sorted_grades = sorted(grades)
    count = len(grades)
    
    # Calculate median
    mid = count // 2
    if count % 2 == 0:
        median = (sorted_grades[mid - 1] + sorted_grades[mid]) / 2
    else:
        median = sorted_grades[mid]
    
    # Count passing grades (>= 10)
    passing = sum(1 for g in grades if g >= 10)
    
    return {
        'count': count,
        'average': round(sum(grades) / count, 2),
        'min': min(grades),
        'max': max(grades),
        'median': median,
        'passing_count': passing,
        'passing_rate': round((passing / count) * 100, 1),
    }


def grade_to_letter(grade):
    """
    Convert numeric grade (1-20) to letter grade.
    
    French grading scale:
    - 16-20: Très Bien (A)
    - 14-15: Bien (B)
    - 12-13: Assez Bien (C)
    - 10-11: Passable (D)
    - 0-9: Insuffisant (F)
    
    Args:
        grade: Numeric grade (1-20)
    
    Returns:
        str: Letter grade
    """
    if grade is None:
        return 'N/A'
    if grade >= 16:
        return 'A'
    if grade >= 14:
        return 'B'
    if grade >= 12:
        return 'C'
    if grade >= 10:
        return 'D'
    return 'F'


def grade_to_description(grade):
    """
    Convert numeric grade to French description.
    
    Args:
        grade: Numeric grade (1-20)
    
    Returns:
        str: Grade description in French
    """
    if grade is None:
        return 'Non noté'
    if grade >= 16:
        return 'Très Bien'
    if grade >= 14:
        return 'Bien'
    if grade >= 12:
        return 'Assez Bien'
    if grade >= 10:
        return 'Passable'
    return 'Insuffisant'


# =============================================================================
# Text Utilities
# =============================================================================

def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (default: 100)
        suffix: Suffix to add if truncated (default: '...')
    
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def get_initials(first_name, last_name):
    """
    Get initials from first and last name.
    
    Args:
        first_name: First name
        last_name: Last name
    
    Returns:
        str: Initials (e.g., 'JD' for 'John Doe')
    """
    initials = ''
    if first_name:
        initials += first_name[0].upper()
    if last_name:
        initials += last_name[0].upper()
    return initials or '??'


# =============================================================================
# Permission Helpers
# =============================================================================

def get_user_classrooms(user):
    """
    Get all classrooms accessible to a user.
    
    Args:
        user: User instance
    
    Returns:
        QuerySet: Classrooms the user can access
    """
    from .models import Classroom, ClassroomMembership, is_teacher
    
    if is_teacher(user):
        return Classroom.objects.filter(teacher=user)
    
    classroom_ids = ClassroomMembership.objects.filter(
        student=user
    ).values_list('classroom_id', flat=True)
    
    return Classroom.objects.filter(id__in=classroom_ids)


def get_user_submissions(user):
    """
    Get all submissions accessible to a user.
    
    Args:
        user: User instance
    
    Returns:
        QuerySet: Submissions the user can access
    """
    from .models import ProjectSubmission, is_teacher
    from django.db.models import Q
    
    if is_teacher(user):
        return ProjectSubmission.objects.filter(classroom__teacher=user)
    
    return ProjectSubmission.objects.filter(
        Q(created_by=user) | Q(collaborators=user)
    ).distinct()


# =============================================================================
# Export Utilities
# =============================================================================

def export_grades_csv(classroom):
    """
    Generate CSV data for classroom grades.
    
    Args:
        classroom: Classroom instance
    
    Returns:
        str: CSV formatted string
    """
    import csv
    from io import StringIO
    from .models import ProjectSubmission
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Student',
        'Email',
        'Project Title',
        'Repository URL',
        'Status',
        'Grade',
        'Submitted At',
        'Teacher Notes'
    ])
    
    # Data
    submissions = ProjectSubmission.objects.filter(
        classroom=classroom
    ).select_related('created_by').order_by('created_by__last_name')
    
    for submission in submissions:
        writer.writerow([
            f"{submission.created_by.first_name} {submission.created_by.last_name}",
            submission.created_by.email,
            submission.title,
            submission.repository_url,
            submission.get_status_display(),
            submission.grade if submission.grade else 'N/A',
            submission.submitted_at.strftime('%Y-%m-%d %H:%M') if submission.submitted_at else 'N/A',
            submission.teacher_notes or ''
        ])
    
    return output.getvalue()
