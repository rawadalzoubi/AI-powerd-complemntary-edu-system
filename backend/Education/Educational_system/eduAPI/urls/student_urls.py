from django.urls import path
from eduAPI.views.student_views import (
    get_student_dashboard_lessons,
    get_student_lesson_detail,
    get_student_lesson_contents,
    get_student_lesson_quizzes,
    start_quiz_attempt,
    submit_quiz_answer,
    complete_quiz_attempt
)

urlpatterns = [
    # Student dashboard endpoints
    path('dashboard/lessons/', get_student_dashboard_lessons, name='student-dashboard-lessons'),
    # Student lesson detail endpoint
    path('lessons/<int:lesson_id>/', get_student_lesson_detail, name='student-lesson-detail'),
    # Student lesson content endpoint
    path('lessons/<int:lesson_id>/contents/', get_student_lesson_contents, name='student-lesson-contents'),
    # Student lesson quizzes endpoint
    path('lessons/<int:lesson_id>/quizzes/', get_student_lesson_quizzes, name='student-lesson-quizzes'),
    
    # Quiz attempt routes
    path('quizzes/<int:quiz_id>/attempt/', start_quiz_attempt, name='start-quiz-attempt'),
    path('quiz-attempts/<int:attempt_id>/submit-answer/', submit_quiz_answer, name='submit-quiz-answer'),
    path('quiz-attempts/<int:attempt_id>/complete/', complete_quiz_attempt, name='complete-quiz-attempt'),
] 