from django.urls import path
from eduAPI.views.lessons_views import (
    LessonListView, LessonDetailView, 
    LessonContentListView, LessonContentDetailView,
    QuizListView, QuizDetailView,
    QuestionListView, QuestionDetailView,
    AnswerListView, AnswerDetailView,
    dashboard_stats,
    filter_lessons,
    assign_lesson_to_student
)

urlpatterns = [
    # Dashboard statistics
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    
    # Lesson routes
    path('lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:lesson_id>/', LessonDetailView.as_view(), name='lesson-detail'),
    
    # Lesson content routes
    path('lessons/<int:lesson_id>/contents/', LessonContentListView.as_view(), name='lesson-content-list'),
    path('contents/<int:content_id>/', LessonContentDetailView.as_view(), name='lesson-content-detail'),
    
    # Quiz routes
    path('lessons/<int:lesson_id>/quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('quizzes/<int:quiz_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    
    # Question routes
    path('quizzes/<int:quiz_id>/questions/', QuestionListView.as_view(), name='question-list'),
    path('questions/<int:question_id>/', QuestionDetailView.as_view(), name='question-detail'),
    
    # Answer routes
    path('questions/<int:question_id>/answers/', AnswerListView.as_view(), name='answer-list'),
    path('answers/<int:answer_id>/', AnswerDetailView.as_view(), name='answer-detail'),
    
    # Advisor routes
    path('advisor/lessons/filter/', filter_lessons, name='filter-lessons'),
    path('advisor/lessons/assign/', assign_lesson_to_student, name='assign-lesson'),
] 