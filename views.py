# views.py
"""
University Project Submission Platform - Views (Class-Based Views Only)

Architecture Decisions:
- All views use Django's CBVs (ListView, CreateView, UpdateView, DetailView, DeleteView, FormView)
- Permission enforcement at both view level (mixins) and queryset level (get_queryset)
- Custom mixins for role-based access control
- Pagination implemented on all list views
- Clean separation between student and teacher views
"""

from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView,
    FormView,
    TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import Http404, HttpResponseForbidden
from django.db.models import Q, Count

from .models import (
    Classroom, 
    ClassroomMembership, 
    ProjectSubmission,
    TeacherProfile,
    is_teacher,
    is_student,
    is_classroom_member,
    is_classroom_teacher
)
from .forms import (
    StudentRegistrationForm,
    TeacherRegistrationForm,
    ClassroomCreateForm,
    ClassroomUpdateForm,
    JoinClassroomForm,
    ProjectSubmissionCreateForm,
    ProjectSubmissionUpdateForm,
    ProjectSubmitForm,
    GradeSubmissionForm,
    SubmissionFilterForm,
    ClassroomFilterForm
)


# =============================================================================
# Custom Mixins for Role-Based Access Control
# =============================================================================

class TeacherRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be a teacher.
    Returns 403 Forbidden if not a teacher.
    """
    def test_func(self):
        return is_teacher(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, "You must be a teacher to access this page.")
        return redirect('dashboard')


class StudentRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be a student (not a teacher).
    """
    def test_func(self):
        return is_student(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, "This page is only for students.")
        return redirect('dashboard')


class ClassroomMemberRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be a member of the classroom.
    Expects classroom_pk in URL kwargs.
    """
    def test_func(self):
        classroom_pk = self.kwargs.get('classroom_pk') or self.kwargs.get('pk')
        classroom = get_object_or_404(Classroom, pk=classroom_pk)
        
        # Teachers of the classroom have access
        if classroom.teacher == self.request.user:
            return True
        
        # Students who are members have access
        return is_classroom_member(self.request.user, classroom)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have access to this classroom.")
        return redirect('dashboard')


class ClassroomTeacherRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be the teacher of the classroom.
    """
    def test_func(self):
        classroom_pk = self.kwargs.get('classroom_pk') or self.kwargs.get('pk')
        classroom = get_object_or_404(Classroom, pk=classroom_pk)
        return classroom.teacher == self.request.user
    
    def handle_no_permission(self):
        messages.error(self.request, "Only the classroom teacher can perform this action.")
        return redirect('dashboard')


# =============================================================================
# Authentication Views
# =============================================================================

class CustomLoginView(LoginView):
    """Custom login view with redirect logic"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = 'login'


class StudentRegisterView(CreateView):
    """Registration view for students"""
    template_name = 'accounts/register_student.html'
    form_class = StudentRegistrationForm
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome, {user.first_name}! Your student account has been created.")
        return redirect(self.success_url)


class TeacherRegisterView(CreateView):
    """Registration view for teachers"""
    template_name = 'accounts/register_teacher.html'
    form_class = TeacherRegistrationForm
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome, {user.first_name}! Your teacher account has been created.")
        return redirect(self.success_url)


# =============================================================================
# Dashboard View
# =============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard view.
    Shows different content based on user role.
    """
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['is_teacher'] = is_teacher(user)
        
        if is_teacher(user):
            # Teacher dashboard data
            context['classrooms'] = Classroom.objects.filter(
                teacher=user
            ).annotate(
                student_count=Count('memberships'),
                submission_count=Count('submissions')
            ).order_by('-created_at')[:5]
            
            context['pending_submissions'] = ProjectSubmission.objects.filter(
                classroom__teacher=user,
                status='SUBMITTED',
                grade__isnull=True
            ).select_related('classroom', 'created_by').order_by('-submitted_at')[:10]
            
            context['total_classrooms'] = Classroom.objects.filter(teacher=user).count()
            context['total_submissions'] = ProjectSubmission.objects.filter(
                classroom__teacher=user
            ).count()
            context['pending_grading'] = ProjectSubmission.objects.filter(
                classroom__teacher=user,
                status='SUBMITTED',
                grade__isnull=True
            ).count()
        else:
            # Student dashboard data
            memberships = ClassroomMembership.objects.filter(
                student=user
            ).select_related('classroom', 'classroom__teacher').order_by('-joined_at')[:5]
            
            context['memberships'] = memberships
            
            # Get student's submissions
            context['my_submissions'] = ProjectSubmission.objects.filter(
                Q(created_by=user) | Q(collaborators=user)
            ).distinct().select_related('classroom').order_by('-created_at')[:5]
            
            context['total_classrooms'] = ClassroomMembership.objects.filter(student=user).count()
            context['total_submissions'] = ProjectSubmission.objects.filter(
                Q(created_by=user) | Q(collaborators=user)
            ).distinct().count()
        
        return context


# =============================================================================
# Classroom Views
# =============================================================================

class ClassroomListView(LoginRequiredMixin, ListView):
    """
    List view for classrooms.
    Teachers see their classrooms; students see classrooms they've joined.
    """
    model = Classroom
    template_name = 'classrooms/classroom_list.html'
    context_object_name = 'classrooms'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        if is_teacher(user):
            queryset = Classroom.objects.filter(teacher=user)
        else:
            # Students see classrooms they're members of
            classroom_ids = ClassroomMembership.objects.filter(
                student=user
            ).values_list('classroom_id', flat=True)
            queryset = Classroom.objects.filter(id__in=classroom_ids)
        
        # Apply filters
        queryset = queryset.annotate(
            student_count=Count('memberships'),
            submission_count=Count('submissions')
        )
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(subject__icontains=search)
            )
        
        # Active filter
        is_active = self.request.GET.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_teacher'] = is_teacher(self.request.user)
        context['filter_form'] = ClassroomFilterForm(self.request.GET)
        return context


class ClassroomDetailView(LoginRequiredMixin, ClassroomMemberRequiredMixin, DetailView):
    """
    Detail view for a classroom.
    Shows different information based on user role.
    """
    model = Classroom
    template_name = 'classrooms/classroom_detail.html'
    context_object_name = 'classroom'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.object
        user = self.request.user
        
        context['is_teacher'] = is_teacher(user)
        context['is_classroom_teacher'] = classroom.teacher == user
        
        if is_teacher(user) and classroom.teacher == user:
            # Teacher sees all submissions
            context['submissions'] = ProjectSubmission.objects.filter(
                classroom=classroom
            ).select_related('created_by').order_by('-submitted_at', '-created_at')
            
            context['students'] = ClassroomMembership.objects.filter(
                classroom=classroom
            ).select_related('student').order_by('-joined_at')
        else:
            # Student sees only their submission (if any)
            context['my_submission'] = ProjectSubmission.objects.filter(
                classroom=classroom,
                created_by=user
            ).first()
            
            # Check if student is a collaborator on any submission
            context['collaborated_submission'] = ProjectSubmission.objects.filter(
                classroom=classroom,
                collaborators=user
            ).exclude(created_by=user).first()
        
        return context


class ClassroomCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    Create view for classrooms.
    Only teachers can create classrooms.
    """
    model = Classroom
    form_class = ClassroomCreateForm
    template_name = 'classrooms/classroom_form.html'
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, f"Classroom '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('classroom_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Classroom'
        context['button_text'] = 'Create Classroom'
        return context


class ClassroomUpdateView(LoginRequiredMixin, ClassroomTeacherRequiredMixin, UpdateView):
    """
    Update view for classrooms.
    Only the classroom teacher can update.
    """
    model = Classroom
    form_class = ClassroomUpdateForm
    template_name = 'classrooms/classroom_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f"Classroom '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('classroom_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Classroom'
        context['button_text'] = 'Save Changes'
        return context


class ClassroomDeleteView(LoginRequiredMixin, ClassroomTeacherRequiredMixin, DeleteView):
    """
    Delete view for classrooms.
    Only the classroom teacher can delete.
    """
    model = Classroom
    template_name = 'classrooms/classroom_confirm_delete.html'
    success_url = reverse_lazy('classroom_list')
    
    def delete(self, request, *args, **kwargs):
        classroom = self.get_object()
        messages.success(request, f"Classroom '{classroom.title}' has been deleted.")
        return super().delete(request, *args, **kwargs)


class JoinClassroomView(LoginRequiredMixin, StudentRequiredMixin, FormView):
    """
    Form view for students to join a classroom using a join code.
    """
    template_name = 'classrooms/join_classroom.html'
    form_class = JoinClassroomForm
    
    def form_valid(self, form):
        classroom = form.get_classroom()
        user = self.request.user
        
        # Check if already a member
        if ClassroomMembership.objects.filter(classroom=classroom, student=user).exists():
            messages.warning(self.request, f"You are already a member of '{classroom.title}'.")
            return redirect('classroom_detail', pk=classroom.pk)
        
        # Create membership
        ClassroomMembership.objects.create(classroom=classroom, student=user)
        messages.success(self.request, f"You have successfully joined '{classroom.title}'!")
        return redirect('classroom_detail', pk=classroom.pk)


class LeaveClassroomView(LoginRequiredMixin, StudentRequiredMixin, DeleteView):
    """
    View for students to leave a classroom.
    """
    model = ClassroomMembership
    template_name = 'classrooms/leave_classroom_confirm.html'
    
    def get_object(self, queryset=None):
        classroom_pk = self.kwargs.get('pk')
        return get_object_or_404(
            ClassroomMembership,
            classroom_id=classroom_pk,
            student=self.request.user
        )
    
    def get_success_url(self):
        return reverse_lazy('classroom_list')
    
    def delete(self, request, *args, **kwargs):
        membership = self.get_object()
        classroom_title = membership.classroom.title
        
        # Check if student has a submission
        has_submission = ProjectSubmission.objects.filter(
            classroom=membership.classroom,
            created_by=request.user
        ).exists()
        
        if has_submission:
            messages.error(request, "You cannot leave a classroom where you have a project submission.")
            return redirect('classroom_detail', pk=membership.classroom.pk)
        
        messages.success(request, f"You have left '{classroom_title}'.")
        return super().delete(request, *args, **kwargs)


# =============================================================================
# Project Submission Views
# =============================================================================

class SubmissionListView(LoginRequiredMixin, ListView):
    """
    List view for project submissions.
    Teachers see submissions from their classrooms.
    Students see their own submissions and collaborations.
    """
    model = ProjectSubmission
    template_name = 'submissions/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        if is_teacher(user):
            # Teachers see all submissions from their classrooms
            queryset = ProjectSubmission.objects.filter(
                classroom__teacher=user
            )
        else:
            # Students see submissions they created or collaborated on
            queryset = ProjectSubmission.objects.filter(
                Q(created_by=user) | Q(collaborators=user)
            ).distinct()
        
        queryset = queryset.select_related('classroom', 'created_by')
        
        # Apply filters from form
        filter_form = SubmissionFilterForm(
            self.request.GET,
            user=user,
            is_teacher=is_teacher(user)
        )
        queryset = filter_form.filter_queryset(queryset)
        
        return queryset.order_by('-submitted_at', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_teacher'] = is_teacher(self.request.user)
        context['filter_form'] = SubmissionFilterForm(
            self.request.GET,
            user=self.request.user,
            is_teacher=is_teacher(self.request.user)
        )
        return context


class SubmissionDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for a project submission.
    Access restricted to teacher, creator, and collaborators.
    """
    model = ProjectSubmission
    template_name = 'submissions/submission_detail.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        return ProjectSubmission.objects.select_related(
            'classroom', 'created_by', 'classroom__teacher'
        ).prefetch_related('collaborators')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Check permissions
        if not obj.can_user_view(self.request.user):
            raise Http404("You don't have permission to view this submission.")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object
        user = self.request.user
        
        context['is_teacher'] = is_teacher(user)
        context['is_classroom_teacher'] = submission.classroom.teacher == user
        context['is_creator'] = submission.created_by == user
        context['can_edit'] = submission.can_user_edit(user)
        context['can_grade'] = submission.classroom.teacher == user
        
        return context


class SubmissionCreateView(LoginRequiredMixin, StudentRequiredMixin, CreateView):
    """
    Create view for project submissions.
    Only students who are members of the classroom can create submissions.
    """
    model = ProjectSubmission
    form_class = ProjectSubmissionCreateForm
    template_name = 'submissions/submission_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.classroom = get_object_or_404(Classroom, pk=kwargs['classroom_pk'])
        
        # Check if user is a member
        if not is_classroom_member(request.user, self.classroom):
            messages.error(request, "You must be a member of this classroom to create a submission.")
            return redirect('classroom_detail', pk=self.classroom.pk)
        
        # Check if user already has a submission
        if ProjectSubmission.objects.filter(classroom=self.classroom, created_by=request.user).exists():
            messages.warning(request, "You already have a submission in this classroom.")
            return redirect('classroom_detail', pk=self.classroom.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['classroom'] = self.classroom
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.classroom = self.classroom
        form.instance.created_by = self.request.user
        messages.success(self.request, "Project submission created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('submission_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = self.classroom
        context['title'] = 'Create Project Submission'
        context['button_text'] = 'Create Submission'
        return context


class SubmissionUpdateView(LoginRequiredMixin, StudentRequiredMixin, UpdateView):
    """
    Update view for project submissions.
    Only the creator can update, and only while status is DRAFT.
    """
    model = ProjectSubmission
    form_class = ProjectSubmissionUpdateForm
    template_name = 'submissions/submission_form.html'
    
    def get_queryset(self):
        # Only allow updating own submissions that are still drafts
        return ProjectSubmission.objects.filter(
            created_by=self.request.user,
            status='DRAFT'
        )
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        if not obj.is_editable():
            messages.error(self.request, "This submission has been submitted and cannot be edited.")
            raise Http404("Submission cannot be edited.")
        
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, "Project submission updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('submission_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = self.object.classroom
        context['title'] = 'Update Project Submission'
        context['button_text'] = 'Save Changes'
        return context


class SubmissionSubmitView(LoginRequiredMixin, StudentRequiredMixin, FormView):
    """
    View to submit a project (change status from DRAFT to SUBMITTED).
    """
    template_name = 'submissions/submission_submit_confirm.html'
    form_class = ProjectSubmitForm
    
    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(
            ProjectSubmission,
            pk=kwargs['pk'],
            created_by=request.user,
            status='DRAFT'
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        self.submission.status = 'SUBMITTED'
        self.submission.save()
        messages.success(self.request, "Your project has been submitted successfully!")
        return redirect('submission_detail', pk=self.submission.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.submission
        return context


class SubmissionDeleteView(LoginRequiredMixin, StudentRequiredMixin, DeleteView):
    """
    Delete view for project submissions.
    Only the creator can delete, and only while status is DRAFT.
    """
    model = ProjectSubmission
    template_name = 'submissions/submission_confirm_delete.html'
    
    def get_queryset(self):
        return ProjectSubmission.objects.filter(
            created_by=self.request.user,
            status='DRAFT'
        )
    
    def get_success_url(self):
        return reverse('classroom_detail', kwargs={'pk': self.object.classroom.pk})
    
    def delete(self, request, *args, **kwargs):
        submission = self.get_object()
        messages.success(request, f"Project '{submission.title}' has been deleted.")
        return super().delete(request, *args, **kwargs)


# =============================================================================
# Teacher Grading Views
# =============================================================================

class TeacherSubmissionListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    """
    List view for teachers to see submissions in a specific classroom.
    Includes filtering and pagination.
    """
    model = ProjectSubmission
    template_name = 'submissions/teacher_submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        self.classroom = get_object_or_404(
            Classroom,
            pk=kwargs['classroom_pk'],
            teacher=request.user
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = ProjectSubmission.objects.filter(
            classroom=self.classroom
        ).select_related('created_by').prefetch_related('collaborators')
        
        # Apply filters
        status = self.request.GET.get('status')
        if status == 'GRADED':
            queryset = queryset.filter(grade__isnull=False)
        elif status in ['DRAFT', 'SUBMITTED']:
            queryset = queryset.filter(status=status)
        
        grade_min = self.request.GET.get('grade_min')
        if grade_min:
            queryset = queryset.filter(grade__gte=int(grade_min))
        
        grade_max = self.request.GET.get('grade_max')
        if grade_max:
            queryset = queryset.filter(grade__lte=int(grade_max))
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(created_by__username__icontains=search) |
                Q(created_by__first_name__icontains=search) |
                Q(created_by__last_name__icontains=search)
            )
        
        return queryset.order_by('-submitted_at', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = self.classroom
        context['filter_form'] = SubmissionFilterForm(
            self.request.GET,
            user=self.request.user,
            is_teacher=True
        )
        
        # Statistics
        all_submissions = ProjectSubmission.objects.filter(classroom=self.classroom)
        context['total_submissions'] = all_submissions.count()
        context['draft_count'] = all_submissions.filter(status='DRAFT').count()
        context['submitted_count'] = all_submissions.filter(status='SUBMITTED').count()
        context['graded_count'] = all_submissions.filter(grade__isnull=False).count()
        context['pending_count'] = all_submissions.filter(
            status='SUBMITTED', grade__isnull=True
        ).count()
        
        return context


class GradeSubmissionView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    """
    View for teachers to grade a submission.
    Only the classroom teacher can grade.
    """
    model = ProjectSubmission
    form_class = GradeSubmissionForm
    template_name = 'submissions/grade_submission.html'
    
    def get_queryset(self):
        return ProjectSubmission.objects.filter(
            classroom__teacher=self.request.user,
            status='SUBMITTED'
        )
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Verify teacher owns the classroom
        if obj.classroom.teacher != self.request.user:
            raise Http404("You don't have permission to grade this submission.")
        
        return obj
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f"Grade saved for '{self.object.title}' - {self.object.grade}/20"
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('teacher_submission_list', kwargs={
            'classroom_pk': self.object.classroom.pk
        })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.object
        return context


# =============================================================================
# Student Views for Viewing Grades
# =============================================================================

class MyGradesView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    """
    View for students to see their grades across all classrooms.
    """
    model = ProjectSubmission
    template_name = 'submissions/my_grades.html'
    context_object_name = 'submissions'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        return ProjectSubmission.objects.filter(
            Q(created_by=user) | Q(collaborators=user)
        ).distinct().select_related(
            'classroom', 'classroom__teacher'
        ).order_by('-submitted_at', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate statistics
        submissions = self.get_queryset()
        graded = submissions.filter(grade__isnull=False)
        
        context['total_submissions'] = submissions.count()
        context['graded_count'] = graded.count()
        context['pending_count'] = submissions.filter(
            status='SUBMITTED', grade__isnull=True
        ).count()
        
        if graded.exists():
            grades = list(graded.values_list('grade', flat=True))
            context['average_grade'] = sum(grades) / len(grades)
            context['highest_grade'] = max(grades)
            context['lowest_grade'] = min(grades)
        
        return context
