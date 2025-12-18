# forms.py
"""
University Project Submission Platform - Forms

Architecture Decisions:
- ModelForms for all CRUD operations (cleaner validation, automatic field generation)
- Custom form for join code (not tied to a model directly)
- Dynamic queryset filtering for collaborators based on classroom membership
- Clean separation between student and teacher forms
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    Classroom, 
    ClassroomMembership, 
    ProjectSubmission, 
    TeacherProfile,
    is_classroom_member
)


# =============================================================================
# Authentication Forms
# =============================================================================

class StudentRegistrationForm(UserCreationForm):
    """
    Registration form for students.
    Uses Django's built-in UserCreationForm with additional fields.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class TeacherRegistrationForm(UserCreationForm):
    """
    Registration form for teachers.
    Creates both User and TeacherProfile.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create teacher profile
            TeacherProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department', '')
            )
        return user


# =============================================================================
# Classroom Forms
# =============================================================================

class ClassroomCreateForm(forms.ModelForm):
    """
    Form for teachers to create classrooms.
    Teacher is set automatically in the view.
    """
    class Meta:
        model = Classroom
        fields = ['title', 'description', 'subject', 'requirements_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter classroom title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the project assignment'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Web Development, Database Systems'
            }),
            'requirements_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class ClassroomUpdateForm(forms.ModelForm):
    """
    Form for teachers to update classroom details.
    Join code and teacher cannot be changed.
    """
    class Meta:
        model = Classroom
        fields = ['title', 'description', 'subject', 'requirements_file', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'requirements_file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JoinClassroomForm(forms.Form):
    """
    Form for students to join a classroom using a join code.
    Not a ModelForm because it doesn't directly create a model instance.
    """
    join_code = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 8-character join code',
            'style': 'text-transform: uppercase;'
        })
    )

    def clean_join_code(self):
        """Validate and normalize join code"""
        code = self.cleaned_data['join_code'].upper().strip()
        
        try:
            classroom = Classroom.objects.get(join_code=code)
        except Classroom.DoesNotExist:
            raise ValidationError("Invalid join code. Please check and try again.")
        
        if not classroom.is_active:
            raise ValidationError("This classroom is no longer accepting new students.")
        
        self.classroom = classroom
        return code

    def get_classroom(self):
        """Return the validated classroom"""
        return getattr(self, 'classroom', None)


# =============================================================================
# Project Submission Forms
# =============================================================================

class ProjectSubmissionCreateForm(forms.ModelForm):
    """
    Form for students to create a project submission.
    Collaborators are filtered to only show classroom members.
    """
    class Meta:
        model = ProjectSubmission
        fields = ['title', 'description', 'repository_url', 'deployed_url', 'collaborators']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your project'
            }),
            'repository_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username/repository'
            }),
            'deployed_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-app.herokuapp.com (optional)'
            }),
            'collaborators': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
        }

    def __init__(self, *args, classroom=None, user=None, **kwargs):
        """
        Initialize form with classroom context.
        Filters collaborators to only show classroom members (excluding current user).
        """
        super().__init__(*args, **kwargs)
        self.classroom = classroom
        self.user = user
        
        if classroom:
            # Get all students in the classroom except the current user
            member_ids = ClassroomMembership.objects.filter(
                classroom=classroom
            ).exclude(
                student=user
            ).values_list('student_id', flat=True)
            
            # Filter collaborators queryset
            self.fields['collaborators'].queryset = User.objects.filter(
                id__in=member_ids
            ).order_by('last_name', 'first_name')
            
            # Update help text
            self.fields['collaborators'].help_text = (
                f"Select collaborators from {classroom.title} members"
            )

    def clean(self):
        """Validate submission constraints"""
        cleaned_data = super().clean()
        
        # Check if user already has a submission in this classroom
        if self.classroom and self.user:
            existing = ProjectSubmission.objects.filter(
                classroom=self.classroom,
                created_by=self.user
            ).exists()
            
            if existing:
                raise ValidationError(
                    "You already have a project submission in this classroom."
                )
        
        return cleaned_data


class ProjectSubmissionUpdateForm(forms.ModelForm):
    """
    Form for students to update their project submission.
    Only available while status is DRAFT.
    """
    class Meta:
        model = ProjectSubmission
        fields = ['title', 'description', 'repository_url', 'deployed_url', 'collaborators']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'repository_url': forms.URLInput(attrs={'class': 'form-control'}),
            'deployed_url': forms.URLInput(attrs={'class': 'form-control'}),
            'collaborators': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form and filter collaborators based on classroom"""
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            classroom = self.instance.classroom
            user = self.instance.created_by
            
            # Get all students in the classroom except the creator
            member_ids = ClassroomMembership.objects.filter(
                classroom=classroom
            ).exclude(
                student=user
            ).values_list('student_id', flat=True)
            
            self.fields['collaborators'].queryset = User.objects.filter(
                id__in=member_ids
            ).order_by('last_name', 'first_name')

    def clean(self):
        """Ensure submission is still in DRAFT status"""
        cleaned_data = super().clean()
        
        if self.instance and self.instance.status != 'DRAFT':
            raise ValidationError(
                "This submission has already been submitted and cannot be edited."
            )
        
        return cleaned_data


class ProjectSubmitForm(forms.Form):
    """
    Simple confirmation form for submitting a project.
    Changes status from DRAFT to SUBMITTED.
    """
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that this project is ready for submission",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


# =============================================================================
# Teacher Grading Forms
# =============================================================================

class GradeSubmissionForm(forms.ModelForm):
    """
    Form for teachers to grade project submissions.
    Only grade and teacher_notes are editable.
    """
    class Meta:
        model = ProjectSubmission
        fields = ['grade', 'teacher_notes']
        widgets = {
            'grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20,
                'placeholder': 'Enter grade (1-20)'
            }),
            'teacher_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter feedback and notes for the student'
            }),
        }

    def clean_grade(self):
        """Validate grade is between 1 and 20"""
        grade = self.cleaned_data.get('grade')
        if grade is not None:
            if grade < 1 or grade > 20:
                raise ValidationError("Grade must be between 1 and 20.")
        return grade


# =============================================================================
# Filter Forms
# =============================================================================

class SubmissionFilterForm(forms.Form):
    """
    Form for filtering project submissions.
    Used by both teachers and students with different field visibility.
    """
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('GRADED', 'Graded'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    grade_min = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min',
            'min': 1,
            'max': 20
        })
    )
    
    grade_max = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max',
            'min': 1,
            'max': 20
        })
    )
    
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.none(),
        required=False,
        empty_label="All Classrooms",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    student = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="All Students",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title...'
        })
    )

    def __init__(self, *args, user=None, is_teacher=False, **kwargs):
        """Initialize form with user context"""
        super().__init__(*args, **kwargs)
        
        if user and is_teacher:
            # Teachers see their classrooms
            self.fields['classroom'].queryset = Classroom.objects.filter(
                teacher=user
            ).order_by('title')
            
            # Teachers can filter by student
            student_ids = ClassroomMembership.objects.filter(
                classroom__teacher=user
            ).values_list('student_id', flat=True).distinct()
            
            self.fields['student'].queryset = User.objects.filter(
                id__in=student_ids
            ).order_by('last_name', 'first_name')
        elif user:
            # Students see classrooms they're members of
            classroom_ids = ClassroomMembership.objects.filter(
                student=user
            ).values_list('classroom_id', flat=True)
            
            self.fields['classroom'].queryset = Classroom.objects.filter(
                id__in=classroom_ids
            ).order_by('title')
            
            # Students don't need to filter by student
            del self.fields['student']

    def filter_queryset(self, queryset):
        """Apply filters to queryset"""
        if self.is_valid():
            # Status filter
            status = self.cleaned_data.get('status')
            if status == 'GRADED':
                queryset = queryset.filter(grade__isnull=False)
            elif status:
                queryset = queryset.filter(status=status)
            
            # Grade range filter
            grade_min = self.cleaned_data.get('grade_min')
            if grade_min:
                queryset = queryset.filter(grade__gte=grade_min)
            
            grade_max = self.cleaned_data.get('grade_max')
            if grade_max:
                queryset = queryset.filter(grade__lte=grade_max)
            
            # Classroom filter
            classroom = self.cleaned_data.get('classroom')
            if classroom:
                queryset = queryset.filter(classroom=classroom)
            
            # Student filter (teachers only)
            student = self.cleaned_data.get('student')
            if student:
                queryset = queryset.filter(created_by=student)
            
            # Search filter
            search = self.cleaned_data.get('search')
            if search:
                queryset = queryset.filter(title__icontains=search)
        
        return queryset


class ClassroomFilterForm(forms.Form):
    """
    Form for filtering classrooms.
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or subject...'
        })
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('true', 'Active'),
            ('false', 'Inactive'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def filter_queryset(self, queryset):
        """Apply filters to queryset"""
        if self.is_valid():
            search = self.cleaned_data.get('search')
            if search:
                queryset = queryset.filter(
                    models.Q(title__icontains=search) |
                    models.Q(subject__icontains=search)
                )
            
            is_active = self.cleaned_data.get('is_active')
            if is_active == 'true':
                queryset = queryset.filter(is_active=True)
            elif is_active == 'false':
                queryset = queryset.filter(is_active=False)
        
        return queryset
