# University Project Submission Platform

A Django-based platform for managing university project submissions, demonstrating mastery of Django fundamentals including Authentication, Forms, CRUD operations, Filtering, and Class-Based Views.

## Architecture Overview

### Design Philosophy

This project follows Django best practices with a focus on:
- **Clean separation of concerns**: Models handle data, Forms handle validation, Views handle logic
- **Role-Based Access Control (RBAC)**: Permissions enforced at both view and queryset levels
- **Class-Based Views only**: Demonstrating proper use of Django's CBV system
- **DRY principles**: Reusable mixins and forms

### Models Architecture

```
┌─────────────────┐     ┌──────────────────┐
│      User       │────▶│  TeacherProfile  │
│  (Django Auth)  │     │   (One-to-One)   │
└────────┬────────┘     └──────────────────┘
         │
         │ ForeignKey (teacher)
         ▼
┌─────────────────┐     ┌──────────────────────┐
│    Classroom    │◀────│  ClassroomMembership │
│                 │     │   (student + joined) │
└────────┬────────┘     └──────────────────────┘
         │                        │
         │ ForeignKey             │ ForeignKey (student)
         ▼                        ▼
┌─────────────────────────────────────────────┐
│            ProjectSubmission                 │
│  - title, description                        │
│  - repository_url (required)                 │
│  - deployed_url (optional)                   │
│  - collaborators (M2M to User)               │
│  - status (DRAFT/SUBMITTED)                  │
│  - grade (1-20, nullable)                    │
│  - teacher_notes                             │
└─────────────────────────────────────────────┘
```

### Key Design Decisions

#### 1. TeacherProfile vs Groups
Instead of using Django's built-in Groups for role management, we use a separate `TeacherProfile` model:
- **Pros**: Cleaner permission checks (`hasattr(user, 'teacher_profile')`), allows teacher-specific fields
- **Cons**: Requires explicit profile creation during registration

#### 2. ClassroomMembership as Explicit Model
Rather than using `ManyToManyField` directly:
- Stores `joined_at` timestamp
- Allows for future metadata (status, notes)
- Cleaner queries for membership validation

#### 3. Status Workflow
Simple two-state workflow: `DRAFT` → `SUBMITTED`
- One-way transition (no reverting to draft)
- `submitted_at` timestamp set automatically
- Editing locked after submission

#### 4. Permission Enforcement
Dual-layer security:
1. **View Level**: Custom mixins (`TeacherRequiredMixin`, `StudentRequiredMixin`, etc.)
2. **Queryset Level**: `get_queryset()` filters data based on user permissions

## File Structure

```
project/
├── models.py          # Data models with validation
├── forms.py           # ModelForms and custom forms
├── views.py           # Class-Based Views only
├── urls.py            # URL routing
├── admin.py           # Admin configuration
└── templates/         # HTML templates (not included)
    ├── accounts/
    │   ├── login.html
    │   ├── register_student.html
    │   └── register_teacher.html
    ├── classrooms/
    │   ├── classroom_list.html
    │   ├── classroom_detail.html
    │   ├── classroom_form.html
    │   ├── classroom_confirm_delete.html
    │   ├── join_classroom.html
    │   └── leave_classroom_confirm.html
    ├── submissions/
    │   ├── submission_list.html
    │   ├── submission_detail.html
    │   ├── submission_form.html
    │   ├── submission_confirm_delete.html
    │   ├── submission_submit_confirm.html
    │   ├── teacher_submission_list.html
    │   ├── grade_submission.html
    │   └── my_grades.html
    └── dashboard.html
```

## Views Summary

### Authentication Views
| View | Type | Description |
|------|------|-------------|
| `CustomLoginView` | LoginView | User login |
| `CustomLogoutView` | LogoutView | User logout |
| `StudentRegisterView` | CreateView | Student registration |
| `TeacherRegisterView` | CreateView | Teacher registration |

### Dashboard
| View | Type | Description |
|------|------|-------------|
| `DashboardView` | TemplateView | Role-based dashboard |

### Classroom Views
| View | Type | Access | Description |
|------|------|--------|-------------|
| `ClassroomListView` | ListView | All | List classrooms (filtered by role) |
| `ClassroomDetailView` | DetailView | Members | Classroom details |
| `ClassroomCreateView` | CreateView | Teachers | Create classroom |
| `ClassroomUpdateView` | UpdateView | Owner | Edit classroom |
| `ClassroomDeleteView` | DeleteView | Owner | Delete classroom |
| `JoinClassroomView` | FormView | Students | Join via code |
| `LeaveClassroomView` | DeleteView | Students | Leave classroom |

### Submission Views
| View | Type | Access | Description |
|------|------|--------|-------------|
| `SubmissionListView` | ListView | All | List submissions |
| `SubmissionDetailView` | DetailView | Participants | Submission details |
| `SubmissionCreateView` | CreateView | Members | Create submission |
| `SubmissionUpdateView` | UpdateView | Creator (Draft) | Edit submission |
| `SubmissionSubmitView` | FormView | Creator (Draft) | Submit project |
| `SubmissionDeleteView` | DeleteView | Creator (Draft) | Delete submission |

### Teacher Grading Views
| View | Type | Access | Description |
|------|------|--------|-------------|
| `TeacherSubmissionListView` | ListView | Teachers | List for grading |
| `GradeSubmissionView` | UpdateView | Teachers | Grade submission |

### Student Grade Views
| View | Type | Access | Description |
|------|------|--------|-------------|
| `MyGradesView` | ListView | Students | View all grades |

## Forms Summary

| Form | Type | Purpose |
|------|------|---------|
| `StudentRegistrationForm` | UserCreationForm | Student signup |
| `TeacherRegistrationForm` | UserCreationForm | Teacher signup |
| `ClassroomCreateForm` | ModelForm | Create classroom |
| `ClassroomUpdateForm` | ModelForm | Edit classroom |
| `JoinClassroomForm` | Form | Join via code |
| `ProjectSubmissionCreateForm` | ModelForm | Create submission |
| `ProjectSubmissionUpdateForm` | ModelForm | Edit submission |
| `ProjectSubmitForm` | Form | Confirm submission |
| `GradeSubmissionForm` | ModelForm | Grade project |
| `SubmissionFilterForm` | Form | Filter submissions |
| `ClassroomFilterForm` | Form | Filter classrooms |

## Filtering & Pagination

### Available Filters
- **Status**: Draft, Submitted, Graded
- **Grade Range**: Min/Max (1-20)
- **Classroom**: Filter by specific classroom
- **Student**: Filter by student (teachers only)
- **Search**: Text search on title

### Pagination
All list views use `paginate_by = 10` with Django's built-in pagination.

## Permission Matrix

| Action | Student | Teacher |
|--------|---------|---------|
| Register | ✓ | ✓ |
| Create Classroom | ✗ | ✓ |
| Join Classroom | ✓ | ✗ |
| View Own Classrooms | ✓ | ✓ |
| Create Submission | ✓ (member) | ✗ |
| Edit Submission | ✓ (creator, draft) | ✗ |
| Submit Project | ✓ (creator, draft) | ✗ |
| View Submission | ✓ (participant) | ✓ (owner) |
| Grade Submission | ✗ | ✓ (owner) |
| View Grades | ✓ (own) | ✓ (all) |

## Setup Instructions

### 1. Add to INSTALLED_APPS
```python
INSTALLED_APPS = [
    ...
    'submissions',  # or your app name
]
```

### 2. Configure Authentication
```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
```

### 3. Include URLs
```python
# project/urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('submissions.urls')),
]
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Create Templates
Create the template files as listed in the file structure above.

## Security Considerations

1. **CSRF Protection**: All forms use Django's CSRF middleware
2. **Permission Checks**: Dual-layer (view + queryset)
3. **Input Validation**: ModelForm validation + custom clean methods
4. **SQL Injection**: Protected by Django ORM
5. **XSS**: Template auto-escaping enabled

## Testing Recommendations

```python
# Example test cases to implement
class ClassroomTests(TestCase):
    def test_only_teachers_can_create_classrooms(self):
        pass
    
    def test_students_can_join_with_valid_code(self):
        pass
    
    def test_invalid_join_code_rejected(self):
        pass

class SubmissionTests(TestCase):
    def test_only_members_can_create_submissions(self):
        pass
    
    def test_submission_locked_after_submit(self):
        pass
    
    def test_collaborators_limited_to_classroom(self):
        pass

class GradingTests(TestCase):
    def test_only_teacher_can_grade(self):
        pass
    
    def test_grade_range_validation(self):
        pass
```

## Future Enhancements

1. **Email Notifications**: Notify students when graded
2. **File Attachments**: Allow file uploads with submissions
3. **Deadline Management**: Add due dates to classrooms
4. **Comments System**: Teacher-student communication
5. **Analytics Dashboard**: Grade statistics and trends
6. **API Endpoints**: REST API for mobile apps

## License

This project is for educational purposes as part of university coursework.
