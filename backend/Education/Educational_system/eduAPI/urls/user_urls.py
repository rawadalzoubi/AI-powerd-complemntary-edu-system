from django.urls import path
from ..views.user_views import (
    register_user,
    verify_email,
    login_user,
    get_user_profile,
    password_reset_request,
    password_reset_confirm,
    validate_reset_token,
    TeacherProfileView,
    StudentProfileView,
    resend_verification_email,
    get_students,
    AdvisorProfileView,
    get_students_by_grade,
    get_student_performance,
    get_student_quiz_answers,
    send_feedback_to_student,
    get_student_feedback
)
from ..views.advisor_views import (
    get_student_lessons,
    assign_lessons_to_student,
    get_advisor_lessons,
    get_student_quiz_attempts,
    delete_student_lesson
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication endpoints
    path('register/', register_user, name='register'),
    path('registration/', register_user, name='user-register'),  # Backwards compatibility
    path('verify-email/', verify_email, name='verify-email'),
    path('login/', login_user, name='login'),
    path('profile/', get_user_profile, name='user-profile'),
    path('resend-verification/', resend_verification_email, name='resend-verification'),
    
    # JWT Token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password reset endpoints
    path('password-reset/request/', password_reset_request, name='password-reset-request'),
    path('password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    path('password-reset/validate/<str:token>/', validate_reset_token, name='validate-reset-token'),
    
    # Teacher profile endpoints
    path('teacher/profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('teacher/profile/<int:teacher_id>/', TeacherProfileView.as_view(), name='teacher-profile-detail'),
    
    # Student profile endpoints
    path('student/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('student/profile/<int:student_id>/', StudentProfileView.as_view(), name='student-profile-detail'),
    
    # Students listing endpoint (for teachers)
    path('students/', get_students, name='get-students'),
    
    # Student quiz answers endpoint (for teachers)
    path('students/<int:student_id>/quiz-answers/', get_student_quiz_answers, name='get-student-quiz-answers'),
    
    # Feedback endpoints
    path('feedback/send/', send_feedback_to_student, name='send-feedback'),
    path('feedback/student/', get_student_feedback, name='get-student-feedback'),
    path('feedback/student/<int:student_id>/', get_student_feedback, name='get-student-feedback-by-id'),
    
    # Advisor profile endpoints
    path('advisor/profile/', AdvisorProfileView.as_view(), name='advisor-profile'),
    path('advisor/profile/<int:advisor_id>/', AdvisorProfileView.as_view(), name='advisor-profile-detail'),
    
    # Advisor student management endpoints
    path('advisor/students/', get_students_by_grade, name='advisor-get-students'),
    path('advisor/students/grade/<str:grade_level>/', get_students_by_grade, name='advisor-get-students-by-grade'),
    path('advisor/students/<int:student_id>/performance/', get_student_performance, name='advisor-get-student-performance'),
    
    # Advisor student lessons endpoints
    path('advisor/students/<int:student_id>/lessons/', get_student_lessons, name='advisor-get-student-lessons'),
    path('advisor/students/<int:student_id>/assign-lessons/', assign_lessons_to_student, name='advisor-assign-lessons'),
    path('advisor/students/<int:student_id>/lessons/<int:lesson_id>/', delete_student_lesson, name='advisor-delete-student-lesson'),
    path('advisor/lessons/', get_advisor_lessons, name='advisor-get-lessons'),
    
    # Advisor student quiz attempts endpoint
    path('advisor/students/<int:student_id>/quiz-attempts/', get_student_quiz_attempts, name='advisor-get-student-quiz-attempts'),
] 