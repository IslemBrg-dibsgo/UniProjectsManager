# models.py
"""
University Project Submission Platform - Models

Architecture Decisions:
- TeacherProfile: One-to-one extension of User to mark teachers (cleaner than groups for this use case)
- Classroom: Represents a single project assignment with unique join code
- ClassroomMembership: Explicit join table for student-classroom relationship with metadata
- ProjectSubmission: Core submission model with status workflow and collaborator support

All models use proper Django conventions with related_name for reverse lookups.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils import timezone
import os


def classroom_file_path(instance, filename):
    """Generate file path for classroom requirement documents"""
    return f'classrooms/{instance.id}/{filename}'


class TeacherProfile(models.Model):
    """
    Extends User to mark teachers.
    
    Design Choice: Using a separate profile model rather than groups because:
    1. Cleaner permission checks (user.teacher_profile exists)
    2. Allows for teacher-specific fields in the future
    3. More explicit than checking group membership
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='teacher_profile'
    )
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'

    def __str__(self):
        return f"Teacher: {self.user.username}"


def generate_join_code():
    """Generate a unique 8-character join code"""
    return get_random_string(8, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')


class Classroom(models.Model):
    """
    Represents one project assignment tied to a teacher and subject.
    
    Key Features:
    - Unique join code for students to join
    - Optional file upload for project requirements (cahier de charges)
    - Each classroom represents exactly one project assignment
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=100, blank=True)
    requirements_file = models.FileField(
        upload_to=classroom_file_path,
        blank=True,
        null=True,
        help_text="Upload project requirements document (PDF, DOCX, etc.)"
    )
    join_code = models.CharField(
        max_length=8, 
        unique=True, 
        default=generate_join_code,
        editable=False
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='taught_classrooms',
        limit_choices_to={'teacher_profile__isnull': False}
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Classroom'
        verbose_name_plural = 'Classrooms'

    def __str__(self):
        return f"{self.title} ({self.join_code})"

    def get_student_count(self):
        """Return the number of students enrolled"""
        return self.memberships.count()

    def get_submission_count(self):
        """Return the number of project submissions"""
        return self.submissions.count()

    def get_submitted_count(self):
        """Return the number of submitted projects"""
        return self.submissions.filter(status='SUBMITTED').count()

    def get_graded_count(self):
        """Return the number of graded projects"""
        return self.submissions.filter(grade__isnull=False).count()


class ClassroomMembership(models.Model):
    """
    Links students to classrooms.
    
    Design Choice: Explicit join table rather than ManyToMany because:
    1. Stores join timestamp
    2. Allows for additional metadata (e.g., student notes, status)
    3. Cleaner queries for membership checks
    """
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='classroom_memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['classroom', 'student']
        ordering = ['-joined_at']
        verbose_name = 'Classroom Membership'
        verbose_name_plural = 'Classroom Memberships'

    def __str__(self):
        return f"{self.student.username} in {self.classroom.title}"

    def clean(self):
        """Validate that teachers cannot join as students"""
        if hasattr(self.student, 'teacher_profile'):
            raise ValidationError("Teachers cannot join classrooms as students.")


class ProjectSubmission(models.Model):
    """
    Represents the actual student work.
    
    Key Features:
    - Status workflow: DRAFT -> SUBMITTED (one-way transition)
    - Collaborators limited to classroom members
    - Grade (1-20) and teacher notes
    - Read-only after submission
    
    Constraints:
    - Only one submission per student per classroom
    - Collaborators must be in the same classroom
    - Cannot edit after submission
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
    ]

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    repository_url = models.URLField(
        help_text="GitHub/GitLab repository URL (required)"
    )
    deployed_url = models.URLField(
        blank=True,
        null=True,
        help_text="Deployed application URL (optional)"
    )
    collaborators = models.ManyToManyField(
        User,
        related_name='collaborated_submissions',
        blank=True,
        help_text="Select collaborators from classroom members"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    grade = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Grade from 1 to 20"
    )
    teacher_notes = models.TextField(
        blank=True,
        help_text="Feedback and notes from the teacher"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_submissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project Submission'
        verbose_name_plural = 'Project Submissions'
        # Ensure one submission per creator per classroom
        unique_together = ['classroom', 'created_by']

    def __str__(self):
        return f"{self.title} - {self.classroom.title}"

    def clean(self):
        """Validate submission constraints"""
        # Validate creator is a member of the classroom
        if not ClassroomMembership.objects.filter(
            classroom=self.classroom,
            student=self.created_by
        ).exists():
            raise ValidationError("You must be a member of this classroom to submit a project.")

    def save(self, *args, **kwargs):
        """Set submitted_at timestamp when status changes to SUBMITTED"""
        if self.status == 'SUBMITTED' and not self.submitted_at:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)

    def is_editable(self):
        """Check if the submission can be edited"""
        return self.status == 'DRAFT'

    def is_graded(self):
        """Check if the submission has been graded"""
        return self.grade is not None

    def can_user_view(self, user):
        """Check if a user can view this submission"""
        # Teacher of the classroom can view
        if self.classroom.teacher == user:
            return True
        # Creator can view
        if self.created_by == user:
            return True
        # Collaborators can view
        if self.collaborators.filter(id=user.id).exists():
            return True
        return False

    def can_user_edit(self, user):
        """Check if a user can edit this submission"""
        if not self.is_editable():
            return False
        return self.created_by == user

    def get_all_participants(self):
        """Get all users involved in this submission (creator + collaborators)"""
        participants = list(self.collaborators.all())
        if self.created_by not in participants:
            participants.append(self.created_by)
        return participants

    def get_grade_display(self):
        """Return formatted grade or status"""
        if self.grade:
            return f"{self.grade}/20"
        elif self.status == 'SUBMITTED':
            return "Pending Grade"
        return "Draft"


# Helper functions for permission checks
def is_teacher(user):
    """Check if user is a teacher"""
    return hasattr(user, 'teacher_profile')


def is_student(user):
    """Check if user is a student (not a teacher)"""
    return not hasattr(user, 'teacher_profile')


def is_classroom_member(user, classroom):
    """Check if user is a member of the classroom"""
    return ClassroomMembership.objects.filter(
        classroom=classroom,
        student=user
    ).exists()


def is_classroom_teacher(user, classroom):
    """Check if user is the teacher of the classroom"""
    return classroom.teacher == user
