# mixins.py
"""
University Project Submission Platform - Reusable Mixins

This module contains reusable mixins for views that provide:
- Role-based access control
- Permission checking
- Common context data
"""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from .models import (
    Classroom,
    ClassroomMembership,
    is_teacher,
    is_student,
    is_classroom_member
)


class TeacherRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be a teacher.
    
    Usage:
        class MyView(LoginRequiredMixin, TeacherRequiredMixin, View):
            ...
    
    Behavior:
        - Returns 403 Forbidden if user is not a teacher
        - Redirects to dashboard with error message
    """
    permission_denied_message = "You must be a teacher to access this page."
    
    def test_func(self):
        return is_teacher(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('dashboard')


class StudentRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be a student (not a teacher).
    
    Usage:
        class MyView(LoginRequiredMixin, StudentRequiredMixin, View):
            ...
    
    Behavior:
        - Returns 403 Forbidden if user is a teacher
        - Redirects to dashboard with error message
    """
    permission_denied_message = "This page is only for students."
    
    def test_func(self):
        return is_student(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('dashboard')


class ClassroomContextMixin:
    """
    Mixin that adds classroom to context.
    
    Expects either:
        - classroom_pk in URL kwargs
        - pk in URL kwargs (for classroom views)
    
    Usage:
        class MyView(ClassroomContextMixin, View):
            ...
    """
    classroom = None
    
    def get_classroom(self):
        """Get the classroom from URL kwargs"""
        if self.classroom is None:
            classroom_pk = self.kwargs.get('classroom_pk') or self.kwargs.get('pk')
            self.classroom = get_object_or_404(Classroom, pk=classroom_pk)
        return self.classroom
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = self.get_classroom()
        return context


class ClassroomMemberRequiredMixin(UserPassesTestMixin, ClassroomContextMixin):
    """
    Mixin that requires the user to be a member of the classroom.
    
    Allows access to:
        - The classroom teacher
        - Students who are members of the classroom
    
    Usage:
        class MyView(LoginRequiredMixin, ClassroomMemberRequiredMixin, View):
            ...
    """
    permission_denied_message = "You don't have access to this classroom."
    
    def test_func(self):
        classroom = self.get_classroom()
        user = self.request.user
        
        # Teachers of the classroom have access
        if classroom.teacher == user:
            return True
        
        # Students who are members have access
        return is_classroom_member(user, classroom)
    
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('dashboard')


class ClassroomTeacherRequiredMixin(UserPassesTestMixin, ClassroomContextMixin):
    """
    Mixin that requires the user to be the teacher of the classroom.
    
    Usage:
        class MyView(LoginRequiredMixin, ClassroomTeacherRequiredMixin, View):
            ...
    """
    permission_denied_message = "Only the classroom teacher can perform this action."
    
    def test_func(self):
        classroom = self.get_classroom()
        return classroom.teacher == self.request.user
    
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('classroom_detail', pk=self.get_classroom().pk)


class SubmissionOwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be the owner (creator) of the submission.
    
    Usage:
        class MyView(LoginRequiredMixin, SubmissionOwnerRequiredMixin, UpdateView):
            model = ProjectSubmission
            ...
    """
    permission_denied_message = "You can only edit your own submissions."
    
    def test_func(self):
        submission = self.get_object()
        return submission.created_by == self.request.user
    
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('submission_list')


class DraftSubmissionRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the submission to be in DRAFT status.
    
    Usage:
        class MyView(LoginRequiredMixin, DraftSubmissionRequiredMixin, UpdateView):
            model = ProjectSubmission
            ...
    """
    permission_denied_message = "This submission has been submitted and cannot be edited."
    
    def test_func(self):
        submission = self.get_object()
        return submission.status == 'DRAFT'
    
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        submission = self.get_object()
        return redirect('submission_detail', pk=submission.pk)


class RoleContextMixin:
    """
    Mixin that adds role information to context.
    
    Adds:
        - is_teacher: Boolean indicating if user is a teacher
        - is_student: Boolean indicating if user is a student
    
    Usage:
        class MyView(RoleContextMixin, View):
            ...
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            context['is_teacher'] = is_teacher(user)
            context['is_student'] = is_student(user)
        else:
            context['is_teacher'] = False
            context['is_student'] = False
        
        return context


class PaginationMixin:
    """
    Mixin that provides consistent pagination settings.
    
    Usage:
        class MyListView(PaginationMixin, ListView):
            ...
    """
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add pagination info for templates
        page_obj = context.get('page_obj')
        if page_obj:
            context['page_range'] = self.get_page_range(page_obj)
        
        return context
    
    def get_page_range(self, page_obj, on_each_side=2, on_ends=1):
        """
        Get a smart page range for pagination.
        Shows pages around current page and at the ends.
        """
        paginator = page_obj.paginator
        current_page = page_obj.number
        num_pages = paginator.num_pages
        
        if num_pages <= 7:
            return range(1, num_pages + 1)
        
        pages = set()
        
        # Pages at the start
        for i in range(1, on_ends + 1):
            pages.add(i)
        
        # Pages at the end
        for i in range(num_pages - on_ends + 1, num_pages + 1):
            pages.add(i)
        
        # Pages around current
        for i in range(
            max(1, current_page - on_each_side),
            min(num_pages + 1, current_page + on_each_side + 1)
        ):
            pages.add(i)
        
        return sorted(pages)


class FilterMixin:
    """
    Mixin that provides filtering functionality.
    
    Usage:
        class MyListView(FilterMixin, ListView):
            filter_form_class = MyFilterForm
            ...
    """
    filter_form_class = None
    
    def get_filter_form(self):
        """Get the filter form instance"""
        if self.filter_form_class:
            return self.filter_form_class(
                self.request.GET,
                user=self.request.user,
                is_teacher=is_teacher(self.request.user)
            )
        return None
    
    def get_queryset(self):
        """Apply filters to queryset"""
        queryset = super().get_queryset()
        
        filter_form = self.get_filter_form()
        if filter_form and hasattr(filter_form, 'filter_queryset'):
            queryset = filter_form.filter_queryset(queryset)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_filter_form()
        return context


class SuccessMessageMixin:
    """
    Mixin that adds success messages after form submission.
    
    Usage:
        class MyCreateView(SuccessMessageMixin, CreateView):
            success_message = "Object created successfully!"
            ...
    """
    success_message = None
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class FormKwargsMixin:
    """
    Mixin that passes additional kwargs to forms.
    
    Usage:
        class MyCreateView(FormKwargsMixin, CreateView):
            def get_form_kwargs(self):
                kwargs = super().get_form_kwargs()
                kwargs['user'] = self.request.user
                return kwargs
    """
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
