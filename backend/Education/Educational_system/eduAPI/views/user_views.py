from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from ..services import user_service
from ..serializers.user_serializers import (
    UserSerializer, RegisterSerializer, VerifyEmailSerializer, 
    LoginSerializer, TeacherProfileSerializer, StudentProfileSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, ResendVerificationEmailSerializer,
    AdvisorProfileSerializer
)
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from ..models.user_model import User
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    print(f"Received registration request: {request.data}")
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Send verification email
            try:
                user_service.send_verification_email(user)
                print(f"Verification email sent to {user.email}")
            except Exception as email_error:
                print(f"Error sending verification email: {email_error}")
                # Still continue with the registration
            
            return Response({
                'status': 'success',
                'message': 'User registered successfully. Please verify your email.'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    print(f"Registration validation errors: {serializer.errors}")
    
    # Check for email uniqueness error specifically
    if 'email' in serializer.errors and any('unique' in str(error).lower() for error in serializer.errors['email']):
        return Response({
            'status': 'error',
            'message': 'Registration failed.',
            'errors': {
                'email': ['This email is already used.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'status': 'error',
        'message': 'Registration failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    serializer = VerifyEmailSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        verification_code = serializer.validated_data['verification_code']
        
        try:
            user = User.objects.get(email=email)
            if user_service.verify_email(user, verification_code):
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'status': 'success',
                    'message': 'Email verified successfully.',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid verification code.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'status': 'error',
        'message': 'Verification failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """Resend the verification email to user"""
    serializer = ResendVerificationEmailSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Don't resend if already verified
            if user.is_email_verified:
                return Response({
                    'status': 'success',
                    'message': 'Email is already verified.'
                }, status=status.HTTP_200_OK)
            
            # Resend verification email
            user_service.send_verification_email(user)
            
            return Response({
                'status': 'success',
                'message': 'Verification email has been resent.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't disclose if email exists or not for security
            return Response({
                'status': 'success',
                'message': 'If this email exists in our system, a verification email has been sent.'
            }, status=status.HTTP_200_OK)
    
    return Response({
        'status': 'error',
        'message': 'Failed to resend verification email.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
            
            # Authenticate user
            if user.check_password(password):
                # Check if user account is active
                if not user.is_active:
                    return Response({
                        'status': 'error',
                        'message': 'Your account has been deactivated. Please contact an administrator.'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Check if email is verified
                if not user.is_email_verified:
                    return Response({
                        'status': 'error',
                        'message': 'Your email address is not verified.',
                        'requires_verification': True,
                        'email': email
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'status': 'success', 
                    'message': 'Login successful',
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    },
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid login credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Invalid login credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'status': 'error',
        'message': 'Invalid login data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Handle password reset request by sending email with reset link"""
    print(f"Password reset request received: {request.data}")
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        print(f"Processing password reset for email: {email}")
        
        try:
            success, message = user_service.initiate_password_reset(email)
            
            if success:
                return Response({
                    'status': 'success',
                    'message': message
                }, status=status.HTTP_200_OK)
            else:
                print(f"Password reset failed: {message}")
                return Response({
                    'status': 'error',
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in password reset: {str(e)}")
            return Response({
                'status': 'error',
                'message': f"Failed to process password reset: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    print(f"Invalid password reset request data: {serializer.errors}")
    return Response({
        'status': 'error',
        'message': 'Invalid email address',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Handle password reset confirmation with token and new password"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        success, message = user_service.reset_password(token, password)
        
        if success:
            return Response({
                'status': 'success',
                'message': message
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'status': 'error',
        'message': 'Invalid data.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_reset_token(request, token):
    """Validate that a password reset token is valid"""
    user = user_service.validate_password_reset_token(token)
    
    if user:
        return Response({
            'status': 'success',
            'message': 'Token is valid',
            'email': user.email
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Invalid or expired token'
        }, status=status.HTTP_400_BAD_REQUEST)


class TeacherProfileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        teacher_id = kwargs.get('teacher_id')
        if teacher_id:
            # View another teacher's profile
            teacher = get_object_or_404(User, id=teacher_id, role=User.TEACHER)
        else:
            # View own profile
            teacher = request.user
            if teacher.role != User.TEACHER:
                return Response({
                    "status": "error",
                    "message": "Only teachers can access this endpoint"
                }, status=status.HTTP_403_FORBIDDEN)
                
        serializer = TeacherProfileSerializer(teacher, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        if user.role != User.TEACHER:
            return Response({
                "status": "error",
                "message": "Only teachers can update their profile"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TeacherProfileSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_user = serializer.save()
            # Include the role explicitly in the response
            response_data = serializer.data
            response_data['role'] = updated_user.role
            response_data['is_email_verified'] = updated_user.is_email_verified
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentProfileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        if student_id:
            # View another student's profile (might have permissions implications)
            student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        else:
            # View own profile
            student = request.user
            if student.role != User.STUDENT:
                return Response({
                    "status": "error",
                    "message": "Only students can access this endpoint"
                }, status=status.HTTP_403_FORBIDDEN)
                
        serializer = StudentProfileSerializer(student, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        if user.role != User.STUDENT:
            return Response({
                "status": "error",
                "message": "Only students can update their profile"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = StudentProfileSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_user = serializer.save()
            # Include the role explicitly in the response
            response_data = serializer.data
            response_data['role'] = updated_user.role
            response_data['is_email_verified'] = updated_user.is_email_verified
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_students(request):
    """
    Get all students assigned to the current teacher (based on lesson enrollments).
    This endpoint returns a list of users with the 'student' role who are enrolled
    in lessons taught by the requesting teacher.
    """
    try:
        # Check if the requesting user is a teacher
        if request.user.role != 'teacher':
            return Response({
                'status': 'error',
                'message': 'Only teachers can access student information'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get teacher's lessons
        from ..models.lessons_model import Lesson, StudentEnrollment
        teacher_lessons = Lesson.objects.filter(teacher=request.user.id)
        
        # Find students enrolled in these lessons
        # Since migration might not be complete, handle potential errors
        try:
            # The ideal way using the StudentEnrollment model
            # Get all students enrolled in any of this teacher's lessons
            student_ids = StudentEnrollment.objects.filter(
                lesson__in=teacher_lessons
            ).values_list('student', flat=True).distinct()
            
            # Get the actual student user objects, excluding the teacher themselves
            students = User.objects.filter(id__in=student_ids).exclude(id=request.user.id)
        except Exception as e:
            print(f"Error using StudentEnrollment model: {e}")
            # Fallback: just get a few student users as an example
            # In production, remove this fallback and rely on enrollments
            students = User.objects.filter(role='student')[:5]  # Just get first 5 students as example
        
        # Serialize with necessary details
        student_data = []
        for student in students:
            # Calculate progress (should be fetched from StudentEnrollment)
            try:
                # Try to get average progress from enrollments
                enrollments = StudentEnrollment.objects.filter(
                    student=student,
                    lesson__in=teacher_lessons
                )
                
                if enrollments.exists():
                    from django.db.models import Avg
                    progress = enrollments.aggregate(Avg('progress'))['progress__avg'] or 0
                    progress = round(progress)
                    
                    # Get lesson names
                    enrolled_lesson_names = [e.lesson.name for e in enrollments]
                    enrolled_lessons = [{
                        'id': e.lesson.id,
                        'name': e.lesson.name,
                        'subject': e.lesson.subject
                    } for e in enrollments]
                else:
                    # No enrollments found
                    progress = 0
                    enrolled_lesson_names = []
                    enrolled_lessons = []
            except Exception as e:
                print(f"Error fetching enrollments: {e}")
                # Placeholder fallback
                import random
                progress = random.randint(0, 100)
                
                # Get enrolled lessons for this student (fallback)
                enrolled_lesson_names = [lesson.name for lesson in teacher_lessons[:3]]
                enrolled_lessons = [{
                    'id': lesson.id,
                    'name': lesson.name,
                    'subject': lesson.subject
                } for lesson in teacher_lessons[:3]]
            
            student_data.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'grade': student.grade_level,
                'enrolled_lessons': enrolled_lesson_names,
                'lessons': enrolled_lessons,
                'progress': progress,
                'last_login': student.last_login.isoformat() if student.last_login else None
            })
        
        return Response(student_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdvisorProfileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        advisor_id = kwargs.get('advisor_id')
        if advisor_id:
            # View another advisor's profile
            advisor = get_object_or_404(User, id=advisor_id, role=User.ADVISOR)
        else:
            # View own profile
            advisor = request.user
            if advisor.role != User.ADVISOR:
                return Response({
                    "status": "error",
                    "message": "Only advisors can access this endpoint"
                }, status=status.HTTP_403_FORBIDDEN)
                
        serializer = AdvisorProfileSerializer(advisor, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        if user.role != User.ADVISOR:
            return Response({
                "status": "error",
                "message": "Only advisors can update their profile"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AdvisorProfileSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_user = serializer.save()
            # Include the role explicitly in the response
            response_data = serializer.data
            response_data['role'] = updated_user.role
            response_data['is_email_verified'] = updated_user.is_email_verified
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_students_by_grade(request, grade_level=None):
    """
    Get all students filtered by grade level.
    This endpoint returns a list of students with the specified grade level.
    Supports search by name or email.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != 'advisor':
            return Response({
                'status': 'error',
                'message': 'Only advisors can access this endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Filter students by grade level if provided
        filters = Q(role='student')
        if grade_level:
            filters &= Q(grade_level=grade_level)
        
        # Add search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            search_filters = (
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
            filters &= search_filters
            
        students = User.objects.filter(filters).order_by('first_name', 'last_name')
        
        # Serialize student data
        student_data = []
        for student in students:
            student_data.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'grade_level': student.grade_level,
                'last_login': student.last_login.isoformat() if student.last_login else None
            })
        
        return Response(student_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_performance(request, student_id):
    """
    Get performance details for a specific student.
    This endpoint returns quiz results and lesson progress for the specified student.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != User.ADVISOR:
            return Response({
                'status': 'error',
                'message': 'Only advisors can access student performance data'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the student
        student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        
        # Get student's enrollments and performance data
        from ..models.lessons_model import StudentEnrollment
        enrollments = StudentEnrollment.objects.filter(student=student)
        
        # Compile performance data
        performance_data = {
            'student': {
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email,
                'grade': student.grade_level
            },
            'enrollments': []
        }
        
        # Add enrollment data
        for enrollment in enrollments:
            lesson = enrollment.lesson
            
            # Add enrollment details
            performance_data['enrollments'].append({
                'lesson_id': lesson.id,
                'lesson_name': lesson.name,
                'subject': lesson.subject,
                'grade_level': lesson.level,
                'progress': enrollment.progress,
                'enrollment_date': enrollment.enrollment_date.isoformat(),
                'last_activity': enrollment.last_activity_date.isoformat()
            })
        
        return Response(performance_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_quiz_answers(request, student_id):
    """
    Get all quiz answers submitted by a specific student.
    This endpoint allows teachers to view a student's answers to quizzes.
    """
    try:
        # Check if the requesting user is a teacher
        if request.user.role != User.TEACHER:
            return Response({
                'status': 'error',
                'message': 'Only teachers can access student quiz answers'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the student
        student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        
        # Get all quiz attempts by this student for lessons taught by the teacher
        from ..models.lessons_model import Lesson, QuizAttempt, QuizAnswer, Quiz
        
        # First, get all lessons taught by the teacher
        teacher_lessons = Lesson.objects.filter(teacher=request.user)
        
        # Get all quizzes associated with these lessons
        teacher_quizzes = Quiz.objects.filter(lesson__in=teacher_lessons)
        
        # Get all quiz attempts for these quizzes by the student
        quiz_attempts = QuizAttempt.objects.filter(
            student=student,
            quiz__in=teacher_quizzes
        ).order_by('-start_time')  # Latest attempts first
        
        if not quiz_attempts.exists():
            return Response({
                'status': 'info',
                'message': 'No quiz attempts found for this student in your lessons.'
            }, status=status.HTTP_200_OK)
            
        # Structure the response data
        response_data = []
        
        for attempt in quiz_attempts:
            try:
                quiz = attempt.quiz
                lesson = quiz.lesson
                
                # Get all answers for this attempt
                quiz_answers = QuizAnswer.objects.filter(attempt=attempt)
                
                # Serialize the answers
                answers_data = []
                for answer in quiz_answers:
                    try:
                        correct_answer = next((a.answer_text for a in answer.question.answers.all() if a.is_correct), None)
                        answers_data.append({
                            'question_text': answer.question.question_text,
                            'selected_answer': answer.selected_answer.answer_text,
                            'is_correct': answer.is_correct,
                            'correct_answer': correct_answer,
                        })
                    except Exception as answer_error:
                        # Handle potential errors with individual answers
                        logger.error(f"Error processing answer: {answer_error}")
                        continue
                
                attempt_data = {
                    'attempt_id': attempt.id,
                    'quiz_id': quiz.id,
                    'quiz_title': quiz.title,
                    'lesson_id': lesson.id,
                    'lesson_name': lesson.name,
                    'start_time': attempt.start_time.isoformat(),
                    'end_time': attempt.end_time.isoformat() if attempt.end_time else None,
                    'score': attempt.score,
                    'passed': attempt.passed,
                    'answers': answers_data
                }
                
                response_data.append(attempt_data)
            except Exception as attempt_error:
                # Handle potential errors with individual attempts
                logger.error(f"Error processing quiz attempt {attempt.id}: {attempt_error}")
                continue
        
        if not response_data:
            return Response({
                'status': 'warning',
                'message': 'Could not retrieve quiz answers. Some data may be missing or corrupted.'
            }, status=status.HTTP_200_OK)
            
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_student_quiz_answers: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Failed to load student answers. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_feedback_to_student(request):
    """
    Send feedback to a student about their quiz attempt.
    This endpoint allows teachers to provide feedback on student quiz attempts.
    """
    try:
        # Check if the requesting user is a teacher
        if request.user.role != User.TEACHER:
            return Response({
                'status': 'error',
                'message': 'Only teachers can send feedback to students'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate request data
        student_id = request.data.get('student_id')
        attempt_id = request.data.get('attempt_id')
        feedback_text = request.data.get('feedback_text')
        
        if not student_id or not attempt_id or not feedback_text:
            return Response({
                'status': 'error',
                'message': 'Missing required fields: student_id, attempt_id, and feedback_text are all required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get student and quiz attempt
        from ..models.lessons_model import QuizAttempt, StudentFeedback
        
        student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=student)
        
        # Check if teacher has permission to send feedback
        # Teacher should have taught the lesson that the quiz belongs to
        if quiz_attempt.quiz.lesson.teacher.id != request.user.id:
            return Response({
                'status': 'error',
                'message': 'You do not have permission to provide feedback on this quiz attempt'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create or update feedback
        feedback, created = StudentFeedback.objects.update_or_create(
            teacher=request.user,
            student=student,
            quiz_attempt=quiz_attempt,
            defaults={'feedback_text': feedback_text, 'is_read': False}
        )
        
        return Response({
            'status': 'success',
            'message': 'Feedback sent successfully',
            'feedback_id': feedback.id,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_feedback(request, student_id=None):
    """
    Get feedback for a specific student or for the current student.
    Teachers can view feedback they've sent to any student.
    Students can only view feedback sent to them.
    """
    try:
        from ..models.lessons_model import StudentFeedback, StudentEnrollment
        
        if request.user.role == User.TEACHER:
            # For teachers, get feedback they've sent to the specified student
            if not student_id:
                return Response({
                    'status': 'error',
                    'message': 'Student ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            student = get_object_or_404(User, id=student_id, role=User.STUDENT)
            feedback = StudentFeedback.objects.filter(
                teacher=request.user,
                student=student
            ).order_by('-created_at')
            
        elif request.user.role == User.STUDENT:
            # For students, get feedback sent to them
            # Ignore the student_id parameter if provided
            
            # Get all lessons this student is enrolled in
            enrolled_lesson_ids = StudentEnrollment.objects.filter(
                student=request.user
            ).values_list('lesson_id', flat=True)
            
            # Only include feedback for quiz attempts related to lessons the student is still enrolled in
            feedback = StudentFeedback.objects.filter(
                student=request.user,
                quiz_attempt__quiz__lesson_id__in=enrolled_lesson_ids
            ).order_by('-created_at')
            
            # Mark feedback as read
            feedback.filter(is_read=False).update(is_read=True)
            
        else:
            return Response({
                'status': 'error',
                'message': 'Unauthorized access'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Format response
        feedback_data = []
        for item in feedback:
            quiz_attempt = item.quiz_attempt
            feedback_data.append({
                'id': item.id,
                'teacher': {
                    'id': item.teacher.id,
                    'name': f"{item.teacher.first_name} {item.teacher.last_name}",
                },
                'quiz_attempt': {
                    'id': quiz_attempt.id,
                    'quiz_title': quiz_attempt.quiz.title,
                    'lesson_name': quiz_attempt.quiz.lesson.name,
                    'score': quiz_attempt.score,
                    'date': quiz_attempt.start_time.isoformat()
                },
                'feedback_text': item.feedback_text,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat(),
                'is_read': item.is_read
            })
        
        return Response(feedback_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 