# managers.py
"""
University Project Submission Platform - Custom Model Managers

Custom managers for common queries and permission-aware querysets.
"""

from django.db import models
from django.db.models import Q, Count


class ClassroomManager(models.Manager):
    """
    Custom manager for Classroom model.
    
    Provides methods for common queries and filtering.
    """
    
    def active(self):
        """Return only active classrooms"""
        return self.filter(is_active=True)
    
    def for_teacher(self, teacher):
        """Return classrooms taught by a specific teacher"""
        return self.filter(teacher=teacher)
    
    def for_student(self, student):
        """Return classrooms a student is a member of"""
        from .models import ClassroomMembership
        classroom_ids = ClassroomMembership.objects.filter(
            student=student
        ).values_list('classroom_id', flat=True)
        return self.filter(id__in=classroom_ids)
    
    def with_counts(self):
        """Return classrooms with student and submission counts"""
        return self.annotate(
            student_count=Count('memberships', distinct=True),
            submission_count=Count('submissions', distinct=True)
        )
    
    def search(self, query):
        """Search classrooms by title, description, or subject"""
        return self.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__icontains=query)
        )


class ClassroomMembershipManager(models.Manager):
    """
    Custom manager for ClassroomMembership model.
    """
    
    def for_classroom(self, classroom):
        """Return memberships for a specific classroom"""
        return self.filter(classroom=classroom)
    
    def for_student(self, student):
        """Return memberships for a specific student"""
        return self.filter(student=student)
    
    def is_member(self, student, classroom):
        """Check if a student is a member of a classroom"""
        return self.filter(student=student, classroom=classroom).exists()


class ProjectSubmissionManager(models.Manager):
    """
    Custom manager for ProjectSubmission model.
    
    Provides methods for permission-aware queries.
    """
    
    def for_teacher(self, teacher):
        """Return submissions from classrooms taught by a teacher"""
        return self.filter(classroom__teacher=teacher)
    
    def for_student(self, student):
        """Return submissions created by or collaborated on by a student"""
        return self.filter(
            Q(created_by=student) | Q(collaborators=student)
        ).distinct()
    
    def for_classroom(self, classroom):
        """Return submissions for a specific classroom"""
        return self.filter(classroom=classroom)
    
    def visible_to(self, user):
        """
        Return submissions visible to a user.
        
        Teachers can see all submissions in their classrooms.
        Students can see their own submissions and collaborations.
        """
        from .models import is_teacher
        
        if is_teacher(user):
            return self.for_teacher(user)
        return self.for_student(user)
    
    def drafts(self):
        """Return draft submissions"""
        return self.filter(status='DRAFT')
    
    def submitted(self):
        """Return submitted submissions"""
        return self.filter(status='SUBMITTED')
    
    def graded(self):
        """Return graded submissions"""
        return self.filter(grade__isnull=False)
    
    def pending_grade(self):
        """Return submitted but not yet graded submissions"""
        return self.filter(status='SUBMITTED', grade__isnull=True)
    
    def with_details(self):
        """Return submissions with related data prefetched"""
        return self.select_related(
            'classroom',
            'classroom__teacher',
            'created_by'
        ).prefetch_related('collaborators')
    
    def search(self, query):
        """Search submissions by title or description"""
        return self.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    def in_grade_range(self, min_grade=None, max_grade=None):
        """Filter submissions by grade range"""
        queryset = self.all()
        if min_grade is not None:
            queryset = queryset.filter(grade__gte=min_grade)
        if max_grade is not None:
            queryset = queryset.filter(grade__lte=max_grade)
        return queryset


class SubmissionQuerySet(models.QuerySet):
    """
    Custom QuerySet for chaining submission filters.
    
    Usage:
        ProjectSubmission.objects.for_classroom(classroom).submitted().pending_grade()
    """
    
    def for_classroom(self, classroom):
        return self.filter(classroom=classroom)
    
    def drafts(self):
        return self.filter(status='DRAFT')
    
    def submitted(self):
        return self.filter(status='SUBMITTED')
    
    def graded(self):
        return self.filter(grade__isnull=False)
    
    def pending_grade(self):
        return self.filter(status='SUBMITTED', grade__isnull=True)
    
    def by_student(self, student):
        return self.filter(
            Q(created_by=student) | Q(collaborators=student)
        ).distinct()
    
    def visible_to(self, user):
        from .models import is_teacher
        
        if is_teacher(user):
            return self.filter(classroom__teacher=user)
        return self.by_student(user)


# Create a manager that uses the custom QuerySet
class SubmissionManager(models.Manager):
    """
    Manager that uses SubmissionQuerySet for chainable queries.
    """
    
    def get_queryset(self):
        return SubmissionQuerySet(self.model, using=self._db)
    
    def for_classroom(self, classroom):
        return self.get_queryset().for_classroom(classroom)
    
    def drafts(self):
        return self.get_queryset().drafts()
    
    def submitted(self):
        return self.get_queryset().submitted()
    
    def graded(self):
        return self.get_queryset().graded()
    
    def pending_grade(self):
        return self.get_queryset().pending_grade()
    
    def by_student(self, student):
        return self.get_queryset().by_student(student)
    
    def visible_to(self, user):
        return self.get_queryset().visible_to(user)
