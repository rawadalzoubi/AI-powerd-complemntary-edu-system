from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ..models.user_model import User
from ..models.lessons_model import Lesson, StudentEnrollment, LessonAssignment, Quiz, QuizAttempt, StudentFeedback
from eduAPI.serializers.lessons_serializers import QuizAttemptSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_advisor_lessons(request):
    """
    Get all lessons available for the advisor to assign to students.
    This endpoint returns lessons filtered by level and subject if provided.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != User.ADVISOR:
            return Response({
                'status': 'error',
                'message': 'Only advisors can access this endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters for filtering
        level = request.query_params.get('level')
        subject = request.query_params.get('subject')
        
        # Build query with filters
        query = Q()
        if level:
            query &= Q(level=level)
        if subject:
            query &= Q(subject__icontains=subject)
        
        # Get lessons
        lessons = Lesson.objects.filter(query)
        
        # Prepare response data
        lessons_data = []
        for lesson in lessons:
            lessons_data.append({
                'id': lesson.id,
                'name': lesson.name,
                'subject': lesson.subject,
                'level': lesson.level,
                'level_display': dict(Lesson.GRADE_CHOICES).get(lesson.level, f'Grade {lesson.level}'),
                'created_at': lesson.created_at.isoformat(),
                'teacher': {
                    'id': lesson.teacher.id,
                    'name': f"{lesson.teacher.first_name} {lesson.teacher.last_name}"
                } if lesson.teacher else None
            })
        
        return Response(lessons_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_lessons(request, student_id):
    """
    Get all lessons assigned to a specific student.
    This endpoint returns a list of lessons assigned to the specified student.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != User.ADVISOR:
            return Response({
                'status': 'error',
                'message': 'Only advisors can access this endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the student
        student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        
        # Get lessons assigned to this student (using StudentEnrollment or LessonAssignment)
        try:
            lesson_assignments = LessonAssignment.objects.filter(student=student)
            
            lessons_data = []
            for assignment in lesson_assignments:
                lesson = assignment.lesson
                lessons_data.append({
                    'id': lesson.id,
                    'name': lesson.name,
                    'subject': lesson.subject,
                    'level': lesson.level,
                    'level_display': dict(Lesson.GRADE_CHOICES).get(lesson.level, f'Grade {lesson.level}'),
                    'assigned_date': assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                    'completed': assignment.completed,
                    'advisor_name': f"{assignment.advisor.first_name} {assignment.advisor.last_name}"
                })
            
        except Exception as e:
            # Fallback to enrollments if LessonAssignment is not available
            enrollments = StudentEnrollment.objects.filter(student=student)
            
            lessons_data = []
            for enrollment in enrollments:
                lesson = enrollment.lesson
                lessons_data.append({
                    'id': lesson.id,
                    'name': lesson.name,
                    'subject': lesson.subject,
                    'level': lesson.level,
                    'level_display': dict(Lesson.GRADE_CHOICES).get(lesson.level, f'Grade {lesson.level}'),
                    'assigned_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                    'completed': enrollment.progress >= 100,
                    'progress': enrollment.progress
                })
        
        return Response(lessons_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_lessons_to_student(request, student_id):
    """
    Assign multiple lessons to a specific student.
    This endpoint allows advisors to assign multiple lessons to a student at once.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != User.ADVISOR:
            return Response({
                'status': 'error',
                'message': 'Only advisors can assign lessons to students'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get required data from request
        lesson_ids = request.data.get('lesson_ids', [])
        
        if not lesson_ids:
            return Response({
                'status': 'error',
                'message': 'At least one lesson_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Get the student
        student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        
        # Track assignment status
        successful_assignments = []
        already_assigned = []
        failed_assignments = []
        
        # Process each lesson
        for lesson_id in lesson_ids:
            try:
                # Get the lesson
                lesson = get_object_or_404(Lesson, id=lesson_id)
                
                # Try to create lesson assignment
                try:
                    assignment, created = LessonAssignment.objects.get_or_create(
                        student=student,
                        lesson=lesson,
                        defaults={
                            'advisor': request.user,
                            'completed': False
                        }
                    )
                    
                    if created:
                        successful_assignments.append(lesson.name)
                    else:
                        already_assigned.append(lesson.name)
                        
                except Exception as e:
                    # Fallback to StudentEnrollment
                    enrollment, created = StudentEnrollment.objects.get_or_create(
                        student=student,
                        lesson=lesson,
                        defaults={'progress': 0}
                    )
                    
                    if created:
                        successful_assignments.append(lesson.name)
                    else:
                        already_assigned.append(lesson.name)
                        
            except Exception as e:
                failed_assignments.append(f"{lesson_id}: {str(e)}")
        
        # Prepare response
        message = ""
        if successful_assignments:
            message += f"Successfully assigned {len(successful_assignments)} lessons. "
        if already_assigned:
            message += f"{len(already_assigned)} lessons were already assigned. "
        if failed_assignments:
            message += f"Failed to assign {len(failed_assignments)} lessons."
            
        response_data = {
            'status': 'success' if successful_assignments else 'warning',
            'message': message.strip(),
            'successful_assignments': successful_assignments,
            'already_assigned': already_assigned,
            'failed_assignments': failed_assignments
        }
            
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_quiz_attempts(request, student_id):
    """
    Get quiz attempts for a specific student.
    This endpoint returns all quiz attempts by the specified student.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != 'advisor':
            return Response({
                'status': 'error',
                'message': 'Only advisors can access this endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the student
        student = get_object_or_404(User, id=student_id, role='student')
        
        # Get all quiz attempts for this student
        quiz_attempts = QuizAttempt.objects.filter(student=student)
        
        # Optional: Filter by specific quiz if provided in query params
        quiz_id = request.query_params.get('quiz_id')
        if quiz_id:
            quiz_attempts = quiz_attempts.filter(quiz_id=quiz_id)
            
        # Optional: Filter by specific lesson if provided in query params
        lesson_id = request.query_params.get('lesson_id')
        if lesson_id:
            quiz_attempts = quiz_attempts.filter(quiz__lesson_id=lesson_id)
        
        # Serialize quiz attempts
        serializer = QuizAttemptSerializer(quiz_attempts, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student_lesson(request, student_id, lesson_id):
    """
    Delete a lesson assignment from a student.
    This endpoint allows advisors to remove lessons that were previously assigned to students.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != User.ADVISOR:
            return Response({
                'status': 'error',
                'message': 'Only advisors can delete lesson assignments'
            }, status=status.HTTP_403_FORBIDDEN)
            
        # Get the student and lesson
        student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Track delete status
        deleted = False
        
        # Find all quiz attempts related to this lesson and student
        # Get all quizzes for this lesson
        quizzes = lesson.quizzes.all()
        
        # Get all quiz attempts by this student for these quizzes
        quiz_attempts = QuizAttempt.objects.filter(
            student=student,
            quiz__in=quizzes
        )
        
        # Get and delete all feedback for these attempts instead of deleting the attempts
        feedback_count = 0
        for attempt in quiz_attempts:
            feedback = StudentFeedback.objects.filter(quiz_attempt=attempt)
            feedback_count += feedback.count()
            feedback.delete()
        
        # Instead of deleting quiz attempts, store the lesson name as metadata
        # This will allow historical viewing while preventing feedback from showing
        attempts_count = quiz_attempts.count()
        
        # Try to find and delete LessonAssignment
        try:
            assignment = LessonAssignment.objects.filter(
                student=student,
                lesson=lesson
            ).first()
            
            if assignment:
                assignment.delete()
                deleted = True
        except Exception as e:
            logger.error(f"Error deleting LessonAssignment: {str(e)}")
        
        # Try to find and delete StudentEnrollment
        try:
            enrollment = StudentEnrollment.objects.filter(
                student=student,
                lesson=lesson
            ).first()
            
            if enrollment:
                enrollment.delete()
                deleted = True
        except Exception as e:
            logger.error(f"Error deleting StudentEnrollment: {str(e)}")
            
        if deleted:
            return Response({
                'status': 'success',
                'message': f'Successfully removed lesson "{lesson.name}" from student {student.first_name} {student.last_name}',
                'details': f'Cleaned up {feedback_count} feedback records while preserving {attempts_count} quiz attempts for historical reference.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Lesson assignment not found for this student'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 