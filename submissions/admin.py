"""
Admin Configuration for University Project Submission Platform
Demonstrates: ModelAdmin customization, list displays, filters, search, actions
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, Classroom, ClassroomMembership, ProjectSubmission


# =============================================================================
# USER ADMIN
# =============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Extended User admin with role management"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'role_badge', 'is_active', 'date_joined']
    list_filter = ['is_teacher', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    # Add is_teacher to the fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('is_teacher',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('is_teacher',)}),
    )
    
    @admin.display(description='Role')
    def role_badge(self, obj):
        if obj.is_teacher:
            return format_html('<span style="color: #0d6efd; font-weight: bold;">Teacher</span>')
        return format_html('<span style="color: #198754;">Student</span>')
    
    actions = ['make_teacher', 'make_student']
    
    @admin.action(description='Mark selected users as teachers')
    def make_teacher(self, request, queryset):
        updated = queryset.update(is_teacher=True)
        self.message_user(request, f'{updated} user(s) marked as teachers.')
    
    @admin.action(description='Mark selected users as students')
    def make_student(self, request, queryset):
        updated = queryset.update(is_teacher=False)
        self.message_user(request, f'{updated} user(s) marked as students.')


# =============================================================================
# CLASSROOM ADMIN
# =============================================================================

class ClassroomMembershipInline(admin.TabularInline):
    """Inline for viewing/managing classroom members"""
    model = ClassroomMembership
    extra = 0
    readonly_fields = ['joined_at']
    autocomplete_fields = ['student']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


class ProjectSubmissionInline(admin.TabularInline):
    """Inline for viewing classroom submissions"""
    model = ProjectSubmission
    extra = 0
    readonly_fields = ['title', 'created_by', 'status', 'grade', 'created_at']
    fields = ['title', 'created_by', 'status', 'grade', 'created_at']
    show_change_link = True
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """Classroom admin with member and submission management"""
    
    list_display = ['title', 'teacher', 'join_code_display', 'student_count', 'submission_count', 'created_at']
    list_filter = ['created_at', 'teacher']
    search_fields = ['title', 'description', 'teacher__username', 'teacher__email', 'join_code']
    readonly_fields = ['join_code', 'created_at', 'updated_at']
    autocomplete_fields = ['teacher']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'teacher')
        }),
        ('Files', {
            'fields': ('requirements_file',),
            'classes': ('collapse',)
        }),
        ('Join Information', {
            'fields': ('join_code',),
            'description': 'Students use this code to join the classroom.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ClassroomMembershipInline, ProjectSubmissionInline]
    
    @admin.display(description='Join Code')
    def join_code_display(self, obj):
        return format_html(
            '<code style="background: #f8f9fa; padding: 2px 6px; border-radius: 3px;">{}</code>',
            obj.join_code
        )
    
    @admin.display(description='Students')
    def student_count(self, obj):
        return obj.get_student_count()
    
    @admin.display(description='Submissions')
    def submission_count(self, obj):
        return obj.get_submission_count()
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher')
    
    actions = ['regenerate_join_codes']
    
    @admin.action(description='Regenerate join codes for selected classrooms')
    def regenerate_join_codes(self, request, queryset):
        for classroom in queryset:
            classroom.regenerate_join_code()
        self.message_user(request, f'Regenerated join codes for {queryset.count()} classroom(s).')


# =============================================================================
# CLASSROOM MEMBERSHIP ADMIN
# =============================================================================

@admin.register(ClassroomMembership)
class ClassroomMembershipAdmin(admin.ModelAdmin):
    """Membership admin for managing student enrollments"""
    
    list_display = ['student', 'classroom', 'joined_at']
    list_filter = ['joined_at', 'classroom', 'classroom__teacher']
    search_fields = ['student__username', 'student__email', 'classroom__title']
    autocomplete_fields = ['student', 'classroom']
    readonly_fields = ['joined_at']
    date_hierarchy = 'joined_at'
    ordering = ['-joined_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'classroom')


# =============================================================================
# PROJECT SUBMISSION ADMIN
# =============================================================================

@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    """Submission admin with grading capabilities"""
    
    list_display = [
        'title', 'classroom', 'created_by', 'status_badge', 
        'grade_display', 'collaborator_count', 'created_at'
    ]
    list_filter = ['status', 'classroom', 'classroom__teacher', 'created_at']
    search_fields = [
        'title', 'description', 'created_by__username', 
        'classroom__title', 'repository_url'
    ]
    readonly_fields = ['created_at', 'updated_at', 'submitted_at', 'created_by']
    autocomplete_fields = ['classroom']
    filter_horizontal = ['collaborators']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'classroom', 'created_by')
        }),
        ('Links', {
            'fields': ('repository_url', 'deployed_url')
        }),
        ('Team', {
            'fields': ('collaborators',),
            'description': 'Students collaborating on this project.'
        }),
        ('Status & Grading', {
            'fields': ('status', 'grade', 'teacher_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'DRAFT': '#ffc107',
            'SUBMITTED': '#0d6efd',
        }
        color = colors.get(obj.status, '#6c757d')
        
        if obj.is_graded:
            color = '#198754'
            label = 'Graded'
        else:
            label = obj.get_status_display()
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, label
        )
    
    @admin.display(description='Grade')
    def grade_display(self, obj):
        if obj.grade is None:
            return '-'
        
        # Color code based on grade
        if obj.grade >= 16:
            color = '#198754'  # Green
        elif obj.grade >= 12:
            color = '#0d6efd'  # Blue
        elif obj.grade >= 10:
            color = '#ffc107'  # Yellow
        else:
            color = '#dc3545'  # Red
        
        return format_html(
            '<strong style="color: {};">{}/20</strong>',
            color, obj.grade
        )
    
    @admin.display(description='Collaborators')
    def collaborator_count(self, obj):
        return obj.collaborators.count()
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'classroom', 'created_by'
        ).prefetch_related('collaborators')
    
    actions = ['mark_as_submitted', 'reset_to_draft']
    
    @admin.action(description='Mark selected as submitted')
    def mark_as_submitted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='DRAFT').update(
            status='SUBMITTED',
            submitted_at=timezone.now()
        )
        self.message_user(request, f'{updated} submission(s) marked as submitted.')
    
    @admin.action(description='Reset selected to draft (clear grades)')
    def reset_to_draft(self, request, queryset):
        updated = queryset.update(
            status='DRAFT',
            submitted_at=None,
            grade=None,
            teacher_notes=''
        )
        self.message_user(request, f'{updated} submission(s) reset to draft.')


# =============================================================================
# ADMIN SITE CUSTOMIZATION
# =============================================================================

admin.site.site_header = 'University Project Submission Platform'
admin.site.site_title = 'Project Submission Admin'
admin.site.index_title = 'Administration Dashboard'
