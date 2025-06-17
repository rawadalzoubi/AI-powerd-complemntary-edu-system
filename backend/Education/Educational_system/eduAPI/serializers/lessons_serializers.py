from rest_framework import serializers
from eduAPI.models.lessons_model import Lesson, LessonContent, Quiz, Question, Answer, QuizAttempt, QuizAnswer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=False, required=False)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'points', 'answers']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=False, required=False)
    total_marks = serializers.IntegerField(source='passing_score', required=False)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'passing_score', 'total_marks', 'time_limit_minutes', 'questions']
        extra_kwargs = {
            'passing_score': {'required': False},
        }

class QuizAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    selected_answer_text = serializers.CharField(source='selected_answer.answer_text', read_only=True)
    
    class Meta:
        model = QuizAnswer
        fields = ['id', 'question_text', 'selected_answer_text', 'is_correct']

class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    quiz_answers = QuizAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz_title', 'student_name', 'start_time', 'end_time', 'score', 'passed', 'quiz_answers']

class LessonContentSerializer(serializers.ModelSerializer):
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    
    class Meta:
        model = LessonContent
        fields = ['id', 'content_type', 'content_type_display', 'title', 'file', 'created_at']
        extra_kwargs = {
            'title': {'required': True},
            'content_type': {'required': True}
        }

class LessonSerializer(serializers.ModelSerializer):
    contents = LessonContentSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'description', 'subject', 'level', 'level_display', 'teacher', 'contents', 'quizzes', 'created_at', 'updated_at']
        read_only_fields = ['teacher']

class LessonListSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    content_count = serializers.IntegerField(source='contents.count', read_only=True)
    quiz_count = serializers.IntegerField(source='quizzes.count', read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'description', 'subject', 'level', 'level_display', 'content_count', 'quiz_count', 'created_at']