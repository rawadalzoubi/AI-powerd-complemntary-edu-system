"""
Direct debugging script for the Student Lesson API
"""
import os
import sys
import json
import django
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

# Import models and views
from eduAPI.models import Lesson, StudentEnrollment, User
from eduAPI.views import student_views
from rest_framework.test import APIRequestFactory, force_authenticate

def debug_request():
    """
    Debug a request to the student lesson API directly
    """
    print("\n===== DIRECT API DEBUGGING =====")
    
    # Get all users
    users = User.objects.filter(role='student')[:5]
    print(f"Available students: {', '.join([f'{u.email} (ID: {u.id})' for u in users])}")
    
    # Get all lessons
    lessons = Lesson.objects.all()[:5]
    print(f"Available lessons: {', '.join([f'{l.name} (ID: {l.id})' for l in lessons])}")
    
    # Create a test request
    factory = APIRequestFactory()
    
    # Set parameters - default to lesson 35
    lesson_id = 35
    student_user = users.first() if users.exists() else None
    
    if student_user:
        print(f"\nTesting with user {student_user.email} and lesson ID {lesson_id}")
        
        # Create request to get_student_lesson_detail
        request = factory.get(f'/api/student/lessons/{lesson_id}/')
        
        # Authenticate the request with the student user
        force_authenticate(request, user=student_user)
        
        try:
            print("\nExecuting view function directly...")
            # Call the view function directly
            response = student_views.get_student_lesson_detail(request, lesson_id=lesson_id)
            
            # Print response details
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Content:")
            try:
                content = json.loads(response.content.decode('utf-8'))
                print(json.dumps(content, indent=2))
            except:
                print(response.content)
            
            # Check if enrollment exists
            enrollment = StudentEnrollment.objects.filter(
                student=student_user,
                lesson_id=lesson_id
            ).first()
            
            if enrollment:
                print(f"\nEnrollment exists: Progress={enrollment.progress}%")
            else:
                print("\nNo enrollment found for this user and lesson")
                
        except Exception as e:
            print(f"\nError executing view: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("No student users found - cannot test")

if __name__ == "__main__":
    debug_request() 