# tests.py
"""
University Project Submission Platform - Test Suite

Comprehensive tests for models, forms, views, and permissions.
Run with: python manage.py test
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    TeacherProfile,
    Classroom,
    ClassroomMembership,
    ProjectSubmission,
    is_teacher,
    is_student,
    is_classroom_member
)
from .forms import (
    StudentRegistrationForm,
    TeacherRegistrationForm,
    JoinClassroomForm,
    ProjectSubmissionCreateForm,
    GradeSubmissionForm
)


# =============================================================================
# Test Helpers
# =============================================================================

class TestHelperMixin:
    """Mixin with helper methods for creating test data"""
    
    def create_student(self, username='student', password='testpass123'):
        """Create a student user"""
        user = User.objects.create_user(
            username=username,
            email=f'{username}@test.com',
            password=password,
            first_name='Test',
            last_name='Student'
        )
        return user
    
    def create_teacher(self, username='teacher', password='testpass123'):
        """Create a teacher user with profile"""
        user = User.objects.create_user(
            username=username,
            email=f'{username}@test.com',
            password=password,
            first_name='Test',
            last_name='Teacher'
        )
        TeacherProfile.objects.create(user=user, department='Computer Science')
        return user
    
    def create_classroom(self, teacher, title='Test Classroom'):
        """Create a classroom"""
        return Classroom.objects.create(
            title=title,
            description='Test description',
            teacher=teacher
        )
    
    def join_classroom(self, student, classroom):
        """Add student to classroom"""
        return ClassroomMembership.objects.create(
            classroom=classroom,
            student=student
        )
    
    def create_submission(self, classroom, student, status='DRAFT'):
        """Create a project submission"""
        return ProjectSubmission.objects.create(
            classroom=classroom,
            title='Test Project',
            description='Test description',
            repository_url='https://github.com/test/repo',
            created_by=student,
            status=status
        )


# =============================================================================
# Model Tests
# =============================================================================

class TeacherProfileModelTest(TestCase, TestHelperMixin):
    """Tests for TeacherProfile model"""
    
    def test_teacher_profile_creation(self):
        """Test creating a teacher profile"""
        teacher = self.create_teacher()
        self.assertTrue(hasattr(teacher, 'teacher_profile'))
        self.assertEqual(str(teacher.teacher_profile), f"Teacher: {teacher.username}")
    
    def test_is_teacher_helper(self):
        """Test is_teacher helper function"""
        teacher = self.create_teacher()
        student = self.create_student()
        
        self.assertTrue(is_teacher(teacher))
        self.assertFalse(is_teacher(student))
    
    def test_is_student_helper(self):
        """Test is_student helper function"""
        teacher = self.create_teacher()
        student = self.create_student()
        
        self.assertFalse(is_student(teacher))
        self.assertTrue(is_student(student))


class ClassroomModelTest(TestCase, TestHelperMixin):
    """Tests for Classroom model"""
    
    def test_classroom_creation(self):
        """Test creating a classroom"""
        teacher = self.create_teacher()
        classroom = self.create_classroom(teacher)
        
        self.assertEqual(classroom.teacher, teacher)
        self.assertEqual(len(classroom.join_code), 8)
        self.assertTrue(classroom.is_active)
    
    def test_unique_join_code(self):
        """Test that each classroom has a unique join code"""
        teacher = self.create_teacher()
        classroom1 = self.create_classroom(teacher, 'Classroom 1')
        classroom2 = self.create_classroom(teacher, 'Classroom 2')
        
        self.assertNotEqual(classroom1.join_code, classroom2.join_code)
    
    def test_student_count(self):
        """Test get_student_count method"""
        teacher = self.create_teacher()
        classroom = self.create_classroom(teacher)
        
        self.assertEqual(classroom.get_student_count(), 0)
        
        student1 = self.create_student('student1')
        student2 = self.create_student('student2')
        self.join_classroom(student1, classroom)
        self.join_classroom(student2, classroom)
        
        self.assertEqual(classroom.get_student_count(), 2)


class ClassroomMembershipModelTest(TestCase, TestHelperMixin):
    """Tests for ClassroomMembership model"""
    
    def test_membership_creation(self):
        """Test creating a membership"""
        teacher = self.create_teacher()
        student = self.create_student()
        classroom = self.create_classroom(teacher)
        
        membership = self.join_classroom(student, classroom)
        
        self.assertEqual(membership.student, student)
        self.assertEqual(membership.classroom, classroom)
        self.assertIsNotNone(membership.joined_at)
    
    def test_unique_membership(self):
        """Test that a student can only join a classroom once"""
        teacher = self.create_teacher()
        student = self.create_student()
        classroom = self.create_classroom(teacher)
        
        self.join_classroom(student, classroom)
        
        with self.assertRaises(Exception):
            self.join_classroom(student, classroom)
    
    def test_is_classroom_member_helper(self):
        """Test is_classroom_member helper function"""
        teacher = self.create_teacher()
        student1 = self.create_student('student1')
        student2 = self.create_student('student2')
        classroom = self.create_classroom(teacher)
        
        self.join_classroom(student1, classroom)
        
        self.assertTrue(is_classroom_member(student1, classroom))
        self.assertFalse(is_classroom_member(student2, classroom))


class ProjectSubmissionModelTest(TestCase, TestHelperMixin):
    """Tests for ProjectSubmission model"""
    
    def test_submission_creation(self):
        """Test creating a submission"""
        teacher = self.create_teacher()
        student = self.create_student()
        classroom = self.create_classroom(teacher)
        self.join_classroom(student, classroom)
        
        submission = self.create_submission(classroom, student)
        
        self.assertEqual(submission.status, 'DRAFT')
        self.assertIsNone(submission.grade)
        self.assertTrue(submission.is_editable())
    
    def test_submission_status_change(self):
        """Test changing submission status"""
        teacher = self.create_teacher()
        student = self.create_student()
        classroom = self.create_classroom(teacher)
        self.join_classroom(student, classroom)
        
        submission = self.create_submission(classroom, student)
        self.assertIsNone(submission.submitted_at)
        
        submission.status = 'SUBMITTED'
        submission.save()
        
        self.assertIsNotNone(submission.submitted_at)
        self.assertFalse(submission.is_editable())
    
    def test_unique_submission_per_classroom(self):
        """Test that a student can only have one submission per classroom"""
        teacher = self.create_teacher()
        student = self.create_student()
        classroom = self.create_classroom(teacher)
        self.join_classroom(student, classroom)
        
        self.create_submission(classroom, student)
        
        with self.assertRaises(Exception):
            self.create_submission(classroom, student)
    
    def test_can_user_view(self):
        """Test can_user_view method"""
        teacher = self.create_teacher()
        student1 = self.create_student('student1')
        student2 = self.create_student('student2')
        student3 = self.create_student('student3')
        classroom = self.create_classroom(teacher)
        
        self.join_classroom(student1, classroom)
        self.join_classroom(student2, classroom)
        
        submission = self.create_submission(classroom, student1)
        submission.collaborators.add(student2)
        
        # Creator can view
        self.assertTrue(submission.can_user_view(student1))
        # Collaborator can view
        self.assertTrue(submission.can_user_view(student2))
        # Teacher can view
        self.assertTrue(submission.can_user_view(teacher))
        # Non-participant cannot view
        self.assertFalse(submission.can_user_view(student3))
    
    def test_grade_validation(self):
        """Test grade range validation"""
        teacher = self.create_teacher()
        student = self.create_student()
        classroom = self.create_classroom(teacher)
        self.join_classroom(student, classroom)
        
        submission = self.create_submission(classroom, student, status='SUBMITTED')
        
        # Valid grade
        submission.grade = 15
        submission.full_clean()  # Should not raise
        
        # Invalid grade (too high)
        submission.grade = 25
        with self.assertRaises(ValidationError):
            submission.full_clean()
        
        # Invalid grade (too low)
        submission.grade = 0
        with self.assertRaises(ValidationError):
            submission.full_clean()


# =============================================================================
# Form Tests
# =============================================================================

class StudentRegistrationFormTest(TestCase):
    """Tests for StudentRegistrationForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'newstudent',
            'email': 'student@test.com',
            'first_name': 'New',
            'last_name': 'Student',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = StudentRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'username': 'newstudent',
            'email': 'student@test.com',
            'first_name': 'New',
            'last_name': 'Student',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = StudentRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class JoinClassroomFormTest(TestCase, TestHelperMixin):
    """Tests for JoinClassroomForm"""
    
    def test_valid_join_code(self):
        """Test form with valid join code"""
        teacher = self.create_teacher()
        classroom = self.create_classroom(teacher)
        
        form = JoinClassroomForm(data={'join_code': classroom.join_code})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_classroom(), classroom)
    
    def test_invalid_join_code(self):
        """Test form with invalid join code"""
        form = JoinClassroomForm(data={'join_code': 'INVALID1'})
        self.assertFalse(form.is_valid())
        self.assertIn('join_code', form.errors)
    
    def test_inactive_classroom(self):
        """Test form with inactive classroom"""
        teacher = self.create_teacher()
        classroom = self.create_classroom(teacher)
        classroom.is_active = False
        classroom.save()
        
        form = JoinClassroomForm(data={'join_code': classroom.join_code})
        self.assertFalse(form.is_valid())


class GradeSubmissionFormTest(TestCase, TestHelperMixin):
    """Tests for GradeSubmissionForm"""
    
    def test_valid_grade(self):
        """Test form with valid grade"""
        form = GradeSubmissionForm(data={
            'grade': 15,
            'teacher_notes': 'Good work!'
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_grade_too_high(self):
        """Test form with grade above 20"""
        form = GradeSubmissionForm(data={
            'grade': 25,
            'teacher_notes': ''
        })
        self.assertFalse(form.is_valid())
    
    def test_invalid_grade_too_low(self):
        """Test form with grade below 1"""
        form = GradeSubmissionForm(data={
            'grade': 0,
            'teacher_notes': ''
        })
        self.assertFalse(form.is_valid())


# =============================================================================
# View Tests
# =============================================================================

class AuthenticationViewTest(TestCase, TestHelperMixin):
    """Tests for authentication views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_login_page_loads(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_student_registration(self):
        """Test student registration"""
        response = self.client.post(reverse('register_student'), {
            'username': 'newstudent',
            'email': 'student@test.com',
            'first_name': 'New',
            'last_name': 'Student',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        
        user = User.objects.get(username='newstudent')
        self.assertFalse(hasattr(user, 'teacher_profile'))


class DashboardViewTest(TestCase, TestHelperMixin):
    """Tests for dashboard view"""
    
    def setUp(self):
        self.client = Client()
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_student_dashboard(self):
        """Test student sees correct dashboard"""
        student = self.create_student()
        self.client.login(username='student', password='testpass123')
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_teacher'])
    
    def test_teacher_dashboard(self):
        """Test teacher sees correct dashboard"""
        teacher = self.create_teacher()
        self.client.login(username='teacher', password='testpass123')
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_teacher'])


class ClassroomViewTest(TestCase, TestHelperMixin):
    """Tests for classroom views"""
    
    def setUp(self):
        self.client = Client()
        self.teacher = self.create_teacher()
        self.student = self.create_student()
    
    def test_only_teachers_can_create_classroom(self):
        """Test that only teachers can create classrooms"""
        # Student tries to create
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('classroom_create'))
        self.assertEqual(response.status_code, 302)  # Redirect (permission denied)
        
        # Teacher can create
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(reverse('classroom_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_classroom_creation(self):
        """Test classroom creation by teacher"""
        self.client.login(username='teacher', password='testpass123')
        
        response = self.client.post(reverse('classroom_create'), {
            'title': 'New Classroom',
            'description': 'Test description',
            'subject': 'Web Development'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Classroom.objects.filter(title='New Classroom').exists())
    
    def test_join_classroom(self):
        """Test student joining classroom"""
        classroom = self.create_classroom(self.teacher)
        
        self.client.login(username='student', password='testpass123')
        response = self.client.post(reverse('classroom_join'), {
            'join_code': classroom.join_code
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(
            ClassroomMembership.objects.filter(
                classroom=classroom,
                student=self.student
            ).exists()
        )


class SubmissionViewTest(TestCase, TestHelperMixin):
    """Tests for submission views"""
    
    def setUp(self):
        self.client = Client()
        self.teacher = self.create_teacher()
        self.student = self.create_student()
        self.classroom = self.create_classroom(self.teacher)
        self.join_classroom(self.student, self.classroom)
    
    def test_only_members_can_create_submission(self):
        """Test that only classroom members can create submissions"""
        non_member = self.create_student('nonmember')
        
        self.client.login(username='nonmember', password='testpass123')
        response = self.client.get(
            reverse('submission_create', kwargs={'classroom_pk': self.classroom.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect (permission denied)
        
        self.client.login(username='student', password='testpass123')
        response = self.client.get(
            reverse('submission_create', kwargs={'classroom_pk': self.classroom.pk})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_submission_creation(self):
        """Test submission creation"""
        self.client.login(username='student', password='testpass123')
        
        response = self.client.post(
            reverse('submission_create', kwargs={'classroom_pk': self.classroom.pk}),
            {
                'title': 'My Project',
                'description': 'Project description',
                'repository_url': 'https://github.com/test/repo'
            }
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(
            ProjectSubmission.objects.filter(
                classroom=self.classroom,
                created_by=self.student
            ).exists()
        )
    
    def test_cannot_edit_submitted_project(self):
        """Test that submitted projects cannot be edited"""
        submission = self.create_submission(self.classroom, self.student, status='SUBMITTED')
        
        self.client.login(username='student', password='testpass123')
        response = self.client.get(
            reverse('submission_update', kwargs={'pk': submission.pk})
        )
        
        self.assertEqual(response.status_code, 404)  # Not found (filtered out)


class GradingViewTest(TestCase, TestHelperMixin):
    """Tests for grading views"""
    
    def setUp(self):
        self.client = Client()
        self.teacher = self.create_teacher()
        self.student = self.create_student()
        self.classroom = self.create_classroom(self.teacher)
        self.join_classroom(self.student, self.classroom)
        self.submission = self.create_submission(
            self.classroom, self.student, status='SUBMITTED'
        )
    
    def test_only_teacher_can_grade(self):
        """Test that only the classroom teacher can grade"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(
            reverse('submission_grade', kwargs={'pk': self.submission.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect (permission denied)
        
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(
            reverse('submission_grade', kwargs={'pk': self.submission.pk})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_grading_submission(self):
        """Test grading a submission"""
        self.client.login(username='teacher', password='testpass123')
        
        response = self.client.post(
            reverse('submission_grade', kwargs={'pk': self.submission.pk}),
            {
                'grade': 18,
                'teacher_notes': 'Excellent work!'
            }
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.grade, 18)
        self.assertEqual(self.submission.teacher_notes, 'Excellent work!')


# =============================================================================
# Permission Tests
# =============================================================================

class PermissionTest(TestCase, TestHelperMixin):
    """Tests for permission enforcement"""
    
    def setUp(self):
        self.client = Client()
        self.teacher1 = self.create_teacher('teacher1')
        self.teacher2 = self.create_teacher('teacher2')
        self.student1 = self.create_student('student1')
        self.student2 = self.create_student('student2')
        
        self.classroom = self.create_classroom(self.teacher1)
        self.join_classroom(self.student1, self.classroom)
    
    def test_other_teacher_cannot_edit_classroom(self):
        """Test that other teachers cannot edit a classroom"""
        self.client.login(username='teacher2', password='testpass123')
        
        response = self.client.get(
            reverse('classroom_update', kwargs={'pk': self.classroom.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect (permission denied)
    
    def test_student_cannot_see_other_submissions(self):
        """Test that students cannot see other students' submissions"""
        submission = self.create_submission(self.classroom, self.student1, status='SUBMITTED')
        
        # Student2 is not in the classroom
        self.client.login(username='student2', password='testpass123')
        response = self.client.get(
            reverse('submission_detail', kwargs={'pk': submission.pk})
        )
        self.assertEqual(response.status_code, 404)  # Not found
    
    def test_collaborator_can_view_submission(self):
        """Test that collaborators can view the submission"""
        self.join_classroom(self.student2, self.classroom)
        submission = self.create_submission(self.classroom, self.student1)
        submission.collaborators.add(self.student2)
        
        self.client.login(username='student2', password='testpass123')
        response = self.client.get(
            reverse('submission_detail', kwargs={'pk': submission.pk})
        )
        self.assertEqual(response.status_code, 200)


# =============================================================================
# Filtering Tests
# =============================================================================

class FilteringTest(TestCase, TestHelperMixin):
    """Tests for filtering functionality"""
    
    def setUp(self):
        self.client = Client()
        self.teacher = self.create_teacher()
        self.classroom = self.create_classroom(self.teacher)
        
        # Create multiple students and submissions
        for i in range(5):
            student = self.create_student(f'student{i}')
            self.join_classroom(student, self.classroom)
            submission = self.create_submission(self.classroom, student)
            if i < 3:
                submission.status = 'SUBMITTED'
                submission.save()
            if i < 2:
                submission.grade = 10 + i * 3
                submission.save()
    
    def test_status_filter(self):
        """Test filtering by status"""
        self.client.login(username='teacher', password='testpass123')
        
        # Filter submitted
        response = self.client.get(
            reverse('teacher_submission_list', kwargs={'classroom_pk': self.classroom.pk}),
            {'status': 'SUBMITTED'}
        )
        self.assertEqual(len(response.context['submissions']), 3)
        
        # Filter draft
        response = self.client.get(
            reverse('teacher_submission_list', kwargs={'classroom_pk': self.classroom.pk}),
            {'status': 'DRAFT'}
        )
        self.assertEqual(len(response.context['submissions']), 2)
    
    def test_grade_range_filter(self):
        """Test filtering by grade range"""
        self.client.login(username='teacher', password='testpass123')
        
        response = self.client.get(
            reverse('teacher_submission_list', kwargs={'classroom_pk': self.classroom.pk}),
            {'grade_min': 12}
        )
        self.assertEqual(len(response.context['submissions']), 1)


# =============================================================================
# Pagination Tests
# =============================================================================

class PaginationTest(TestCase, TestHelperMixin):
    """Tests for pagination"""
    
    def setUp(self):
        self.client = Client()
        self.teacher = self.create_teacher()
        
        # Create 15 classrooms
        for i in range(15):
            self.create_classroom(self.teacher, f'Classroom {i}')
    
    def test_classroom_list_pagination(self):
        """Test classroom list is paginated"""
        self.client.login(username='teacher', password='testpass123')
        
        response = self.client.get(reverse('classroom_list'))
        self.assertEqual(len(response.context['classrooms']), 10)  # paginate_by = 10
        self.assertTrue(response.context['is_paginated'])
        
        # Second page
        response = self.client.get(reverse('classroom_list'), {'page': 2})
        self.assertEqual(len(response.context['classrooms']), 5)
