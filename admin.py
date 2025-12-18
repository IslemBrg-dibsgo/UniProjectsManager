# admin.py
"""
University Project Submission Platform - Admin Configuration

Provides Django admin interface for managing all models.
Useful for initial setup and debugging.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
    TeacherProfile,
    Classroom,
    ClassroomMembership,
    ProjectSubmission
)


# =============================================================================
# Inline Admin Classes
# =============================================================================

class TeacherProfileInline(admin.StackedInline):
    """Inline admin for TeacherProfile on User admin"""
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'


class ClassroomMembershipInline(admin.TabularInline):
    """Inline admin for memberships on Classroom admin"""
    model = ClassroomMembership
    extra = 0
    readonly_fields = ['joined_at']
    autocomplete_fields = ['student']


class ProjectSubmissionInline(admin.TabularInline):
    """Inline admin for submissions on Classroom admin"""
    model = ProjectSubmission
    extra = 0
    readonly_fields = ['created_at', 'submitted_at']
    fields = ['title', 'created_by', 'status', 'grade', 'created_at']


# =============================================================================
# Custom User Admin
# =============================================================================

class CustomUserAdmin(UserAdmin):
    """Extended User admin with TeacherProfile inline"""
    inlines = [TeacherProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_teacher', 'is_active']
    list_filter = ['is_active', 'is_staff', 'teacher_profile']
    
    def is_teacher(self, obj):
        return hasattr(obj, 'teacher_profile')
    is_teacher.boolean = True
    is_teacher.short_description = 'Teacher'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# =============================================================================
# Model Admin Classes
# =============================================================================

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin for TeacherProfile model"""
    list_display = ['user', 'department', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """Admin for Classroom model"""
    list_display = ['title', 'teacher', 'join_code', 'student_count', 'submission_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'teacher']
    search_fields = ['title', 'description', 'subject', 'join_code', 'teacher__username']
    readonly_fields = ['join_code', 'created_at', 'updated_at']
    autocomplete_fields = ['teacher']
    inlines = [ClassroomMembershipInline, ProjectSubmissionInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'subject')
        }),
        ('Teacher & Access', {
            'fields': ('teacher', 'join_code', 'is_active')
        }),
        ('Files', {
            'fields': ('requirements_file',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def student_count(self, obj):
        return obj.get_student_count()
    student_count.short_description = 'Students'
    
    def submission_count(self, obj):
        return obj.get_submission_count()
    submission_count.short_description = 'Submissions'


@admin.register(ClassroomMembership)
class ClassroomMembershipAdmin(admin.ModelAdmin):
    """Admin for ClassroomMembership model"""
    list_display = ['student', 'classroom', 'joined_at']
    list_filter = ['joined_at', 'classroom']
    search_fields = ['student__username', 'student__email', 'classroom__title']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['student', 'classroom']


@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    """Admin for ProjectSubmission model"""
    list_display = ['title', 'classroom', 'created_by', 'status', 'grade_display', 'created_at', 'submitted_at']
    list_filter = ['status', 'grade', 'created_at', 'submitted_at', 'classroom']
    search_fields = ['title', 'description', 'created_by__username', 'classroom__title']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at']
    autocomplete_fields = ['classroom', 'created_by']
    filter_horizontal = ['collaborators']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'classroom')
        }),
        ('Links', {
            'fields': ('repository_url', 'deployed_url')
        }),
        ('Team', {
            'fields': ('created_by', 'collaborators')
        }),
        ('Status & Grading', {
            'fields': ('status', 'grade', 'teacher_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def grade_display(self, obj):
        return obj.get_grade_display()
    grade_display.short_description = 'Grade'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'classroom', 'created_by'
        ).prefetch_related('collaborators')


# =============================================================================
# Admin Site Configuration
# =============================================================================

admin.site.site_header = 'University Project Submission Platform'
admin.site.site_title = 'Project Submission Admin'
admin.site.index_title = 'Administration'
