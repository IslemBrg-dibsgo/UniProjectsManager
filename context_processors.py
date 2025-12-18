# context_processors.py
"""
University Project Submission Platform - Context Processors

Custom context processors to add global template context.
"""

from .models import is_teacher, is_student


def user_role(request):
    """
    Add user role information to all templates.
    
    Usage in settings.py:
        TEMPLATES = [
            {
                ...
                'OPTIONS': {
                    'context_processors': [
                        ...
                        'submissions.context_processors.user_role',
                    ],
                },
            },
        ]
    
    Usage in templates:
        {% if is_teacher %}
            <a href="{% url 'classroom_create' %}">Create Classroom</a>
        {% endif %}
    """
    if request.user.is_authenticated:
        return {
            'is_teacher': is_teacher(request.user),
            'is_student': is_student(request.user),
            'user_role': 'teacher' if is_teacher(request.user) else 'student',
        }
    return {
        'is_teacher': False,
        'is_student': False,
        'user_role': None,
    }


def pending_items(request):
    """
    Add counts of pending items for the current user.
    
    For teachers: Count of submissions pending grading
    For students: Count of ungraded submitted projects
    
    Usage in templates:
        {% if pending_grading_count > 0 %}
            <span class="badge">{{ pending_grading_count }}</span>
        {% endif %}
    """
    if not request.user.is_authenticated:
        return {
            'pending_grading_count': 0,
            'pending_grade_count': 0,
        }
    
    from .models import ProjectSubmission
    from django.db.models import Q
    
    user = request.user
    
    if is_teacher(user):
        # Count submissions pending grading in teacher's classrooms
        pending_grading = ProjectSubmission.objects.filter(
            classroom__teacher=user,
            status='SUBMITTED',
            grade__isnull=True
        ).count()
        
        return {
            'pending_grading_count': pending_grading,
            'pending_grade_count': 0,
        }
    else:
        # Count student's submitted but ungraded projects
        pending_grade = ProjectSubmission.objects.filter(
            Q(created_by=user) | Q(collaborators=user),
            status='SUBMITTED',
            grade__isnull=True
        ).distinct().count()
        
        return {
            'pending_grading_count': 0,
            'pending_grade_count': pending_grade,
        }


def navigation_items(request):
    """
    Add navigation items based on user role.
    
    Usage in templates:
        {% for item in nav_items %}
            <a href="{{ item.url }}" class="{% if item.active %}active{% endif %}">
                {{ item.label }}
            </a>
        {% endfor %}
    """
    if not request.user.is_authenticated:
        return {'nav_items': []}
    
    from django.urls import reverse
    
    current_path = request.path
    
    if is_teacher(request.user):
        nav_items = [
            {
                'label': 'Dashboard',
                'url': reverse('dashboard'),
                'icon': 'home',
                'active': current_path == reverse('dashboard'),
            },
            {
                'label': 'My Classrooms',
                'url': reverse('classroom_list'),
                'icon': 'book',
                'active': '/classrooms/' in current_path,
            },
            {
                'label': 'All Submissions',
                'url': reverse('submission_list'),
                'icon': 'file-text',
                'active': current_path == reverse('submission_list'),
            },
        ]
    else:
        nav_items = [
            {
                'label': 'Dashboard',
                'url': reverse('dashboard'),
                'icon': 'home',
                'active': current_path == reverse('dashboard'),
            },
            {
                'label': 'My Classrooms',
                'url': reverse('classroom_list'),
                'icon': 'book',
                'active': '/classrooms/' in current_path,
            },
            {
                'label': 'My Submissions',
                'url': reverse('submission_list'),
                'icon': 'file-text',
                'active': current_path == reverse('submission_list'),
            },
            {
                'label': 'My Grades',
                'url': reverse('my_grades'),
                'icon': 'award',
                'active': current_path == reverse('my_grades'),
            },
            {
                'label': 'Join Classroom',
                'url': reverse('classroom_join'),
                'icon': 'plus-circle',
                'active': current_path == reverse('classroom_join'),
            },
        ]
    
    return {'nav_items': nav_items}
