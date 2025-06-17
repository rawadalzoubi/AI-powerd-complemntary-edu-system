from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADVISOR = 'advisor'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (ADVISOR, 'Advisor'),
    ]
    
    # Grade/Level choices for students
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
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    
    # Password reset fields
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
    
    # Common profile fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)
    
    # Teacher-specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True)
    academic_degree = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    
    # Student-specific fields
    birthdate = models.DateField(blank=True, null=True)
    grade_level = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'role']
    
    def __str__(self):
        return self.email 
        
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}" 