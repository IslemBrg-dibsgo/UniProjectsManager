# urls.py
"""
University Project Submission Platform - URL Configuration

Architecture Decisions:
- RESTful URL structure for clarity
- Namespaced paths for different resources
- Consistent naming convention for views
- Nested URLs where appropriate (e.g., classroom submissions)
"""

from django.urls import path
from . import views

urlpatterns = [
    # ==========================================================================
    # Authentication URLs
    # ==========================================================================
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.StudentRegisterView.as_view(), name='register'),
    path('register/student/', views.StudentRegisterView.as_view(), name='register_student'),
    path('register/teacher/', views.TeacherRegisterView.as_view(), name='register_teacher'),
    
    # ==========================================================================
    # Dashboard
    # ==========================================================================
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard_alt'),
    
    # ==========================================================================
    # Classroom URLs
    # ==========================================================================
    # List all classrooms (filtered by role)
    path('classrooms/', views.ClassroomListView.as_view(), name='classroom_list'),
    
    # Create new classroom (teachers only)
    path('classrooms/create/', views.ClassroomCreateView.as_view(), name='classroom_create'),
    
    # Join classroom via code (students only)
    path('classrooms/join/', views.JoinClassroomView.as_view(), name='classroom_join'),
    
    # Classroom detail
    path('classrooms/<int:pk>/', views.ClassroomDetailView.as_view(), name='classroom_detail'),
    
    # Update classroom (teacher only)
    path('classrooms/<int:pk>/edit/', views.ClassroomUpdateView.as_view(), name='classroom_update'),
    
    # Delete classroom (teacher only)
    path('classrooms/<int:pk>/delete/', views.ClassroomDeleteView.as_view(), name='classroom_delete'),
    
    # Leave classroom (students only)
    path('classrooms/<int:pk>/leave/', views.LeaveClassroomView.as_view(), name='classroom_leave'),
    
    # ==========================================================================
    # Project Submission URLs
    # ==========================================================================
    # List all submissions (filtered by role and permissions)
    path('submissions/', views.SubmissionListView.as_view(), name='submission_list'),
    
    # Create submission in a classroom
    path(
        'classrooms/<int:classroom_pk>/submissions/create/',
        views.SubmissionCreateView.as_view(),
        name='submission_create'
    ),
    
    # Submission detail
    path('submissions/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    
    # Update submission (creator only, draft only)
    path('submissions/<int:pk>/edit/', views.SubmissionUpdateView.as_view(), name='submission_update'),
    
    # Submit project (change status to SUBMITTED)
    path('submissions/<int:pk>/submit/', views.SubmissionSubmitView.as_view(), name='submission_submit'),
    
    # Delete submission (creator only, draft only)
    path('submissions/<int:pk>/delete/', views.SubmissionDeleteView.as_view(), name='submission_delete'),
    
    # ==========================================================================
    # Teacher Grading URLs
    # ==========================================================================
    # List submissions for a classroom (teachers only)
    path(
        'classrooms/<int:classroom_pk>/submissions/',
        views.TeacherSubmissionListView.as_view(),
        name='teacher_submission_list'
    ),
    
    # Grade a submission
    path('submissions/<int:pk>/grade/', views.GradeSubmissionView.as_view(), name='submission_grade'),
    
    # ==========================================================================
    # Student Grade Views
    # ==========================================================================
    path('my-grades/', views.MyGradesView.as_view(), name='my_grades'),
]

# =============================================================================
# URL Pattern Documentation
# =============================================================================
"""
Authentication:
    /login/                                 - Login page
    /logout/                                - Logout
    /register/                              - Student registration (default)
    /register/student/                      - Student registration
    /register/teacher/                      - Teacher registration

Dashboard:
    /                                       - Main dashboard (role-based)
    /dashboard/                             - Alternative dashboard URL

Classrooms:
    /classrooms/                            - List classrooms
    /classrooms/create/                     - Create classroom (teachers)
    /classrooms/join/                       - Join classroom (students)
    /classrooms/<id>/                       - Classroom detail
    /classrooms/<id>/edit/                  - Edit classroom (teachers)
    /classrooms/<id>/delete/                - Delete classroom (teachers)
    /classrooms/<id>/leave/                 - Leave classroom (students)

Submissions:
    /submissions/                           - List all submissions
    /classrooms/<id>/submissions/create/    - Create submission in classroom
    /submissions/<id>/                      - Submission detail
    /submissions/<id>/edit/                 - Edit submission (draft only)
    /submissions/<id>/submit/               - Submit project
    /submissions/<id>/delete/               - Delete submission (draft only)

Teacher Grading:
    /classrooms/<id>/submissions/           - List submissions for grading
    /submissions/<id>/grade/                - Grade a submission

Student Grades:
    /my-grades/                             - View all grades
"""
