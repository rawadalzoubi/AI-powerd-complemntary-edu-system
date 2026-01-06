"""
Comprehensive Models Tests
Tests for model layer to increase coverage
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from eduAPI.models.lessons_model import Lesson, LessonContent, Quiz, Question, Answer, StudentEnrollment, QuizAttempt
from eduAPI.models.live_sessions_models import LiveSession, LiveSessionAssignment
from eduAPI.models.recurring_sessions_models import SessionTemplate, StudentGroup

User = get_user_model()


class TestUserModel(TestCase):
    """Tests for User model"""

    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student'
        )
        self.assertEqual(user.email, 'test@test.com')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.check_password('SecurePass123!'))

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_str(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student'
        )
        self.assertIn('test@test.com', str(user))

    def test_user_full_name(self):
        """Test user full name property"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role='student'
        )
        self.assertEqual(user.get_full_name(), 'Test User')


class TestLessonModel(TestCase):
    """Tests for Lesson model"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

    def test_create_lesson(self):
        """Test creating a lesson"""
        lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.assertEqual(lesson.name, 'Test Lesson')
        self.assertEqual(lesson.teacher, self.teacher)

    def test_lesson_str(self):
        """Test lesson string representation"""
        lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.assertIn('Test Lesson', str(lesson))


class TestQuizModel(TestCase):
    """Tests for Quiz model"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )

    def test_create_quiz(self):
        """Test creating a quiz"""
        quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test Quiz Description'
        )
        self.assertEqual(quiz.title, 'Test Quiz')
        self.assertEqual(quiz.lesson, self.lesson)

    def test_quiz_str(self):
        """Test quiz string representation"""
        quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test Quiz Description'
        )
        self.assertIn('Test Quiz', str(quiz))


class TestQuestionModel(TestCase):
    """Tests for Question model"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test Quiz Description'
        )

    def test_create_question(self):
        """Test creating a question"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2+2?',
            question_type='multiple_choice'
        )
        self.assertEqual(question.question_text, 'What is 2+2?')
        self.assertEqual(question.quiz, self.quiz)


class TestAnswerModel(TestCase):
    """Tests for Answer model"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Test Quiz',
            description='Test Quiz Description'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2+2?',
            question_type='multiple_choice'
        )

    def test_create_answer(self):
        """Test creating an answer"""
        answer = Answer.objects.create(
            question=self.question,
            answer_text='4',
            is_correct=True
        )
        self.assertEqual(answer.answer_text, '4')
        self.assertTrue(answer.is_correct)


class TestStudentEnrollmentModel(TestCase):
    """Tests for StudentEnrollment model"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Student',
            role='student'
        )
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            subject='Math',
            level='5',
            teacher=self.teacher
        )

    def test_create_enrollment(self):
        """Test creating an enrollment"""
        enrollment = StudentEnrollment.objects.create(
            student=self.student,
            lesson=self.lesson,
            progress=50
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.lesson, self.lesson)
        self.assertEqual(enrollment.progress, 50)


class TestLiveSessionModel(TestCase):
    """Tests for LiveSession model"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

    def test_create_live_session(self):
        """Test creating a live session"""
        tomorrow = timezone.now() + timedelta(days=1)
        session = LiveSession.objects.create(
            title='Test Session',
            description='Test Description',
            teacher=self.teacher,
            scheduled_datetime=tomorrow,
            duration_minutes=60,
            subject='Math',
            level='5',
            jitsi_room_name='test-room-123'
        )
        self.assertEqual(session.title, 'Test Session')
        self.assertEqual(session.teacher, self.teacher)

    def test_live_session_str(self):
        """Test live session string representation"""
        tomorrow = timezone.now() + timedelta(days=1)
        session = LiveSession.objects.create(
            title='Test Session',
            description='Test Description',
            teacher=self.teacher,
            scheduled_datetime=tomorrow,
            duration_minutes=60,
            subject='Math',
            level='5',
            jitsi_room_name='test-room-456'
        )
        self.assertIn('Test Session', str(session))


class TestSessionTemplateModel(TestCase):
    """Tests for SessionTemplate model"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

    def test_create_session_template(self):
        """Test creating a session template"""
        start_date = (timezone.now() + timedelta(days=7)).date()
        template = SessionTemplate.objects.create(
            title='Weekly Math Session',
            teacher=self.teacher,
            subject='Math',
            level='5',
            day_of_week=0,  # Monday
            start_time='09:00:00',
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=start_date
        )
        self.assertEqual(template.title, 'Weekly Math Session')
        self.assertEqual(template.teacher, self.teacher)

    def test_session_template_str(self):
        """Test session template string representation"""
        start_date = (timezone.now() + timedelta(days=7)).date()
        template = SessionTemplate.objects.create(
            title='Weekly Math Session',
            teacher=self.teacher,
            subject='Math',
            level='5',
            day_of_week=0,  # Monday
            start_time='09:00:00',
            duration_minutes=60,
            recurrence_type='WEEKLY',
            start_date=start_date
        )
        self.assertIn('Weekly Math Session', str(template))


class TestStudentGroupModel(TestCase):
    """Tests for StudentGroup model"""

    def setUp(self):
        self.advisor = User.objects.create_user(
            username='advisor',
            email='advisor@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='Advisor',
            role='advisor'
        )

    def test_create_student_group(self):
        """Test creating a student group"""
        group = StudentGroup.objects.create(
            name='Grade 5 Section A',
            description='Grade 5 Section A students',
            advisor=self.advisor
        )
        self.assertEqual(group.name, 'Grade 5 Section A')
        self.assertEqual(group.advisor, self.advisor)

    def test_student_group_str(self):
        """Test student group string representation"""
        group = StudentGroup.objects.create(
            name='Grade 5 Section A',
            description='Grade 5 Section A students',
            advisor=self.advisor
        )
        self.assertIn('Grade 5 Section A', str(group))
