"""
URL Configuration for University Project Submission Platform
Demonstrates: Clean URL patterns, namespacing, RESTful design
"""

from django.urls import path, include
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from . import views


# =============================================================================
# AUTHENTICATION URLS
# =============================================================================

auth_urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Password change (for logged-in users)
    path('password/change/', 
         PasswordChangeView.as_view(template_name='registration/password_change.html'),
         name='password_change'),
    path('password/change/done/',
         PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done'),
    
    # Password reset (for forgotten passwords)
    path('password/reset/',
         PasswordResetView.as_view(template_name='registration/password_reset.html'),
         name='password_reset'),
    path('password/reset/done/',
         PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password/reset/complete/',
         PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]


# =============================================================================
# CLASSROOM URLS
# =============================================================================

classroom_urlpatterns = [
    # List and create
    path('', views.ClassroomListView.as_view(), name='classroom_list'),
    path('create/', views.ClassroomCreateView.as_view(), name='classroom_create'),
    path('join/', views.JoinClassroomView.as_view(), name='classroom_join'),
    
    # Detail, update, delete
    path('<int:pk>/', views.ClassroomDetailView.as_view(), name='classroom_detail'),
    path('<int:pk>/edit/', views.ClassroomUpdateView.as_view(), name='classroom_update'),
    path('<int:pk>/delete/', views.ClassroomDeleteView.as_view(), name='classroom_delete'),
    path('<int:pk>/leave/', views.LeaveClassroomView.as_view(), name='classroom_leave'),
    path('<int:pk>/regenerate-code/', views.RegenerateJoinCodeView.as_view(), name='classroom_regenerate_code'),
    
    # Member management
    path('<int:classroom_pk>/members/', views.ClassroomMemberListView.as_view(), name='classroom_members'),
    path('<int:classroom_pk>/members/<int:student_pk>/remove/', 
         views.RemoveMemberView.as_view(), name='classroom_remove_member'),
    
    # Classroom-specific submissions (for teachers)
    path('<int:classroom_pk>/submissions/', 
         views.ClassroomSubmissionListView.as_view(), name='classroom_submissions'),
    
    # Create submission within classroom
    path('<int:classroom_pk>/submit/', 
         views.SubmissionCreateView.as_view(), name='submission_create'),
]


# =============================================================================
# SUBMISSION URLS
# =============================================================================

submission_urlpatterns = [
    # List all submissions (role-aware)
    path('', views.SubmissionListView.as_view(), name='submission_list'),
    
    # Teacher-specific submission list with all classrooms
    path('teacher/', views.TeacherSubmissionListView.as_view(), name='teacher_submissions'),
    
    # Detail, update, delete
    path('<int:pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('<int:pk>/edit/', views.SubmissionUpdateView.as_view(), name='submission_update'),
    path('<int:pk>/delete/', views.SubmissionDeleteView.as_view(), name='submission_delete'),
    
    # Submit action (change status from DRAFT to SUBMITTED)
    path('<int:pk>/submit/', views.SubmissionSubmitView.as_view(), name='submission_submit'),
    
    # Grading (teacher only)
    path('<int:pk>/grade/', views.GradeSubmissionView.as_view(), name='submission_grade'),
]


# =============================================================================
# MAIN URL PATTERNS
# =============================================================================

urlpatterns = [
    # Dashboard (landing page after login)
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Authentication
    path('auth/', include(auth_urlpatterns)),
    
    # Classrooms
    path('classrooms/', include(classroom_urlpatterns)),
    
    # Submissions
    path('submissions/', include(submission_urlpatterns)),
]


# =============================================================================
# URL PATTERN DOCUMENTATION
# =============================================================================

"""
URL Structure Overview:

AUTHENTICATION (/auth/)
-----------------------
GET  /auth/register/                    - Registration form
POST /auth/register/                    - Create new user
GET  /auth/login/                       - Login form
POST /auth/login/                       - Authenticate user
POST /auth/logout/                      - Logout user
GET  /auth/password/change/             - Password change form
POST /auth/password/change/             - Change password
GET  /auth/password/reset/              - Password reset request form
POST /auth/password/reset/              - Send reset email
GET  /auth/password/reset/<uid>/<token>/- Password reset confirmation
POST /auth/password/reset/<uid>/<token>/- Set new password

CLASSROOMS (/classrooms/)
-------------------------
GET  /classrooms/                       - List user's classrooms
GET  /classrooms/create/                - Create classroom form (teacher)
POST /classrooms/create/                - Create new classroom (teacher)
GET  /classrooms/join/                  - Join classroom form (student)
POST /classrooms/join/                  - Join classroom with code (student)
GET  /classrooms/<pk>/                  - Classroom detail
GET  /classrooms/<pk>/edit/             - Edit classroom form (owner)
POST /classrooms/<pk>/edit/             - Update classroom (owner)
POST /classrooms/<pk>/delete/           - Delete classroom (owner)
POST /classrooms/<pk>/leave/            - Leave classroom (student)
POST /classrooms/<pk>/regenerate-code/  - Generate new join code (owner)
GET  /classrooms/<pk>/members/          - List classroom members
POST /classrooms/<pk>/members/<id>/remove/ - Remove member (owner)
GET  /classrooms/<pk>/submissions/      - List classroom submissions (teacher)
GET  /classrooms/<pk>/submit/           - Create submission form (student)
POST /classrooms/<pk>/submit/           - Create submission (student)

SUBMISSIONS (/submissions/)
---------------------------
GET  /submissions/                      - List user's submissions
GET  /submissions/teacher/              - List all submissions (teacher)
GET  /submissions/<pk>/                 - Submission detail
GET  /submissions/<pk>/edit/            - Edit submission form (draft only)
POST /submissions/<pk>/edit/            - Update submission (draft only)
POST /submissions/<pk>/delete/          - Delete submission (draft only)
GET  /submissions/<pk>/submit/          - Submit confirmation form
POST /submissions/<pk>/submit/          - Submit project (draft -> submitted)
GET  /submissions/<pk>/grade/           - Grade form (teacher)
POST /submissions/<pk>/grade/           - Assign grade (teacher)

FILTERING PARAMETERS (GET)
--------------------------
?status=DRAFT|SUBMITTED|GRADED          - Filter by status
?grade_min=1-20                         - Minimum grade filter
?grade_max=1-20                         - Maximum grade filter
?classroom=<id>                         - Filter by classroom
?student=<name>                         - Search by student name
?search=<query>                         - General search (classrooms)
?page=<number>                          - Pagination
"""
