from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from eduAPI.models.lessons_model import Lesson, LessonContent, Quiz, Question, Answer, StudentEnrollment
from eduAPI.serializers.lessons_serializers import (
    LessonSerializer, LessonListSerializer, LessonContentSerializer, 
    QuizSerializer, QuestionSerializer, AnswerSerializer
)
from eduAPI.services.lessons_service import (
    LessonService, LessonContentService, 
    QuizService, QuestionService, AnswerService
)
from ..models.user_model import User
import datetime

class LessonListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all lessons created by the authenticated teacher."""
        lessons = LessonService.get_teacher_lessons(request.user.id)
        serializer = LessonListSerializer(lessons, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new lesson."""
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            lesson = LessonService.create_lesson(serializer.validated_data, request.user.id)
            return Response(LessonSerializer(lesson).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lesson_id):
        """Get details of a specific lesson."""
        lesson = LessonService.get_lesson_by_id(lesson_id, request.user.id)
        if not lesson:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)
    
    def put(self, request, lesson_id):
        """Update a lesson."""
        lesson = LessonService.get_lesson_by_id(lesson_id, request.user.id)
        if not lesson:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LessonSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            updated_lesson = LessonService.update_lesson(lesson_id, serializer.validated_data, request.user.id)
            return Response(LessonSerializer(updated_lesson).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, lesson_id):
        """Delete a lesson."""
        success = LessonService.delete_lesson(lesson_id, request.user.id)
        if not success:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class LessonContentListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, lesson_id):
        """Get all content for a specific lesson."""
        lesson = LessonService.get_lesson_by_id(lesson_id, request.user.id)
        if not lesson:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)
        
        contents = LessonContentService.get_lesson_contents(lesson_id)
        serializer = LessonContentSerializer(contents, many=True)
        return Response(serializer.data)
    
    def post(self, request, lesson_id):
        """Create new lesson content."""
        lesson = LessonService.get_lesson_by_id(lesson_id, request.user.id)
        if not lesson:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)
        
        data_for_serializer = request.data.copy()
        file_from_request = request.FILES.get('file')

        # If 'file' key exists in data_for_serializer and is not an actual UploadedFile instance,
        # it might be from request.POST (e.g. a string), which would cause FileField validation to fail.
        # We remove it so the serializer correctly picks up from request.FILES or handles absence if optional.
        if 'file' in data_for_serializer and not isinstance(data_for_serializer.get('file'), (InMemoryUploadedFile, TemporaryUploadedFile)):
            if file_from_request is None: # If no actual file was uploaded, and 'file' in POST is a string, remove it.
                del data_for_serializer['file']
            # If file_from_request exists, DRF serializer will pick it from request.FILES part of request.data
            # The presence of a non-file 'file' in data_for_serializer (from POST) can be problematic.
            # It's safer to remove if it's not an UploadedFile.
            elif isinstance(data_for_serializer.get('file'), str): # specifically if it's a string from POST
                 del data_for_serializer['file']

        serializer = LessonContentSerializer(data=data_for_serializer, context={'request': request})
        if serializer.is_valid():
            content = LessonContentService.create_content(
                lesson_id, 
                serializer.validated_data, 
                file_from_request # Use the explicitly fetched file
            )
            return Response(LessonContentSerializer(content, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LessonContentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, content_id):
        """Delete lesson content."""
        success = LessonContentService.delete_content(content_id, request.user.id)
        if not success:
            return Response({"detail": "Content not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class QuizListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lesson_id):
        """Get all quizzes for a specific lesson."""
        lesson = LessonService.get_lesson_by_id(lesson_id, request.user.id)
        if not lesson:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)
        
        quizzes = QuizService.get_lesson_quizzes(lesson_id)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)
    
    def post(self, request, lesson_id):
        """Create a new quiz for a lesson."""
        lesson = LessonService.get_lesson_by_id(lesson_id, request.user.id)
        if not lesson:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            quiz = QuizService.create_quiz(lesson_id, serializer.validated_data)
            return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, quiz_id):
        """Get details of a specific quiz."""
        quiz = QuizService.get_quiz_by_id(quiz_id, request.user.id)
        if not quiz:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)
    
    def put(self, request, quiz_id):
        """Update a quiz."""
        quiz = QuizService.get_quiz_by_id(quiz_id, request.user.id)
        if not quiz:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            updated_quiz = QuizService.update_quiz(quiz_id, serializer.validated_data, request.user.id)
            return Response(QuizSerializer(updated_quiz).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, quiz_id):
        """Delete a quiz."""
        success = QuizService.delete_quiz(quiz_id, request.user.id)
        if not success:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class QuestionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, quiz_id):
        """Get all questions for a specific quiz."""
        quiz = QuizService.get_quiz_by_id(quiz_id, request.user.id)
        if not quiz:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        questions = Question.objects.filter(quiz_id=quiz_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    def post(self, request, quiz_id):
        """Create a new question for a quiz."""
        quiz = QuizService.get_quiz_by_id(quiz_id, request.user.id)
        if not quiz:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = QuestionService.create_question(quiz_id, serializer.validated_data)
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, question_id):
        """Get details of a specific question."""
        question = QuestionService.get_question_by_id(question_id, request.user.id)
        if not question:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuestionSerializer(question)
        return Response(serializer.data)
    
    def put(self, request, question_id):
        """Update a question."""
        question = QuestionService.get_question_by_id(question_id, request.user.id)
        if not question:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            updated_question = QuestionService.update_question(question_id, serializer.validated_data, request.user.id)
            return Response(QuestionSerializer(updated_question).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, question_id):
        """Delete a question."""
        success = QuestionService.delete_question(question_id, request.user.id)
        if not success:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class AnswerListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, question_id):
        """Get all answers for a specific question."""
        question = QuestionService.get_question_by_id(question_id, request.user.id)
        if not question:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        answers = Answer.objects.filter(question_id=question_id)
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)
    
    def post(self, request, question_id):
        """Create a new answer for a question."""
        question = QuestionService.get_question_by_id(question_id, request.user.id)
        if not question:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            answer = AnswerService.create_answer(question_id, serializer.validated_data)
            return Response(AnswerSerializer(answer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnswerDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, answer_id):
        """Get details of a specific answer."""
        answer = AnswerService.get_answer_by_id(answer_id, request.user.id)
        if not answer:
            return Response({"detail": "Answer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AnswerSerializer(answer)
        return Response(serializer.data)
    
    def put(self, request, answer_id):
        """Update an answer."""
        answer = AnswerService.get_answer_by_id(answer_id, request.user.id)
        if not answer:
            return Response({"detail": "Answer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AnswerSerializer(answer, data=request.data, partial=True)
        if serializer.is_valid():
            updated_answer = AnswerService.update_answer(answer_id, serializer.validated_data, request.user.id)
            return Response(AnswerSerializer(updated_answer).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, answer_id):
        """Delete an answer."""
        success = AnswerService.delete_answer(answer_id, request.user.id)
        if not success:
            return Response({"detail": "Answer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for the current teacher
    Returns counts of students, lessons, assignments, etc.
    """
    try:
        # Verify the user is a teacher
        if request.user.role != 'teacher':
            return Response({
                'status': 'error',
                'message': 'Only teachers can access dashboard statistics'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get counts from the database
        from ..models.lessons_model import Lesson
        from django.db.models import Count, Sum, Avg
        
        # Count total students
        total_students = User.objects.filter(role='student').count()
        
        # Calculate student trend (placeholder - for a real app, compare to previous period)
        students_last_month = total_students - 2  # Placeholder, simulate an increase
        students_trend = (total_students - students_last_month) / max(students_last_month, 1) * 100 if students_last_month else 0
        
        # Count lessons by this teacher
        total_lessons = Lesson.objects.filter(teacher=request.user.id).count()
        
        # Calculate lesson trend
        # For a real app, you would compare to lessons created last week/month
        lessons_last_week = total_lessons - 1  # Placeholder, simulate an increase
        lessons_trend = (total_lessons - lessons_last_week) / max(lessons_last_week, 1) * 100 if lessons_last_week else 0
        
        # Assignments data
        # This is placeholder - replace with your real assignment model counts
        graded_assignments = 0
        pending_assignments = 0
        
        # Compile stats
        stats = {
            'total_students': total_students,
            'students_trend': round(students_trend, 1),
            'total_lessons': total_lessons,
            'lessons_trend': round(lessons_trend, 1),
            'graded_assignments': graded_assignments,
            'pending_assignments': pending_assignments
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_lessons(request):
    """
    Filter lessons by subject and grade level.
    This endpoint allows advisors to filter lessons based on subject and grade level.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != User.ADVISOR:
            return Response({
                'status': 'error',
                'message': 'Only advisors can access this endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get filter parameters from request
        subject = request.query_params.get('subject', None)
        grade_level = request.query_params.get('grade_level', None)
        
        # Apply filters
        filters = {}
        if subject:
            filters['subject__icontains'] = subject
        if grade_level:
            filters['level'] = grade_level
            
        lessons = Lesson.objects.filter(**filters)
        serializer = LessonListSerializer(lessons, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_lesson_to_student(request):
    """
    Assign a lesson to a specific student.
    This endpoint allows advisors to assign a lesson to a student.
    """
    try:
        # Check if the requesting user is an advisor
        if request.user.role != User.ADVISOR:
            return Response({
                'status': 'error',
                'message': 'Only advisors can assign lessons to students'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get required data from request
        lesson_id = request.data.get('lesson_id')
        student_id = request.data.get('student_id')
        
        if not lesson_id or not student_id:
            return Response({
                'status': 'error',
                'message': 'Both lesson_id and student_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Get the lesson and student
        lesson = get_object_or_404(Lesson, id=lesson_id)
        student = get_object_or_404(User, id=student_id, role=User.STUDENT)
        
        # Check if enrollment already exists
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=student,
            lesson=lesson,
            defaults={'progress': 0}
        )
        
        if not created:
            return Response({
                'status': 'info',
                'message': 'Student is already enrolled in this lesson'
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'success',
            'message': f'Lesson "{lesson.name}" has been successfully assigned to {student.first_name} {student.last_name}'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 