from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Lesson(models.Model):
    GRADE_CHOICES = [
        ('1', '1st Grade'),
        ('2', '2nd Grade'),
        ('3', '3rd Grade'),
        ('4', '4th Grade'),
        ('5', '5th Grade'),
        ('6', '6th Grade'),
        ('7', '7th Grade'),
        ('8', '8th Grade'),
        ('9', '9th Grade'),
        ('10', '10th Grade'),
        ('11', '11th Grade'),
        ('12', '12th Grade'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=255)
    level = models.CharField(max_length=2, choices=GRADE_CHOICES)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject} (Grade {self.level})"

class StudentEnrollment(models.Model):
    """
    Tracks which students are enrolled in which lessons.
    This model allows teachers to see only their students (via lesson enrollments).
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    last_activity_date = models.DateTimeField(auto_now=True)
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        unique_together = ('student', 'lesson')
        
    def __str__(self):
        return f"{self.student.email} enrolled in {self.lesson.name}"

class LessonContent(models.Model):
    """Content associated with a lesson (videos, PDFs, text, etc.)"""
    TYPE_CHOICES = [
        ('VIDEO', 'Video Content'),
        ('PDF', 'PDF Document'),
        ('TEXT', 'Text Content'),
        ('IMAGE', 'Image Content'),
        ('AUDIO', 'Audio Content'),
        ('LINK', 'External Link'),
        ('OTHER', 'Other Content Type')
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file = models.FileField(upload_to='lesson_files/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"

class Quiz(models.Model):
    """Quiz associated with a lesson"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    time_limit_minutes = models.IntegerField(null=True, blank=True)
    passing_score = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.lesson.name}"

class Question(models.Model):
    """Question for a quiz"""
    TYPE_CHOICES = [
        ('SINGLE', 'Single Choice'),
        ('MULTIPLE', 'Multiple Choice'),
        ('TRUE_FALSE', 'True/False'),
        ('TEXT', 'Text Answer')
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='SINGLE')
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question_text[:50]

class Answer(models.Model):
    """Possible answer for a question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.answer_text[:50]

class LessonAssignment(models.Model):
    """
    Tracks lessons assigned by advisors to students.
    Different from StudentEnrollment as it represents an advisor's assignment action.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assigned_to')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'lesson')
    
    def __str__(self):
        return f"{self.lesson.name} assigned to {self.student.first_name} {self.student.last_name}"
    
    def save(self, *args, **kwargs):
        # Call the "real" save() method
        super().save(*args, **kwargs)
        
        # Check if there's already an enrollment for this student-lesson pair
        from eduAPI.models import StudentEnrollment
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=self.student,
            lesson=self.lesson,
            defaults={
                'progress': 0,
            }
        )
        
        # If we're updating an existing assignment and it's marked as completed,
        # also update the enrollment to 100% progress
        if not created and self.completed and enrollment.progress < 100:
            enrollment.progress = 100
            enrollment.save()

class QuizAttempt(models.Model):
    """Records a student's attempt at a quiz"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.email}'s attempt on {self.quiz.title}"

class QuizAnswer(models.Model):
    """Records a student's answer to a question in a quiz attempt"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='quiz_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Answer to {self.question.question_text[:30]} in {self.attempt}"

class StudentFeedback(models.Model):
    """Feedback from teacher to student about quiz performance"""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_feedback')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedback')
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='feedback')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Feedback from {self.teacher.first_name} {self.teacher.last_name} to {self.student.first_name} {self.student.last_name}"