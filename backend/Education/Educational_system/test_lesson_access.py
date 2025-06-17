"""
Quick script to test lesson access directly
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

# Import models after Django setup
from eduAPI.models import Lesson, StudentEnrollment, User
from eduAPI.serializers import LessonSerializer
from django.core.exceptions import ObjectDoesNotExist

def test_lesson_access(lesson_id=35, user_email="rawadalzoubi@gmail.com"):
    """
    Test if we can access a lesson directly from the database
    """
    print(f"\n=== Testing access to lesson {lesson_id} for {user_email} ===")
    
    try:
        # Check if lesson exists
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            print(f"✅ Found lesson: {lesson.name} (ID: {lesson.id})")
        except ObjectDoesNotExist:
            print(f"❌ Lesson with ID {lesson_id} not found in database")
            return
        
        # Check if user exists
        try:
            user = User.objects.get(email=user_email)
            print(f"✅ Found user: {user.email} (ID: {user.id}, Role: {user.role})")
        except ObjectDoesNotExist:
            print(f"❌ User with email {user_email} not found in database")
            return
        
        # Check enrollment
        enrollment = StudentEnrollment.objects.filter(student=user, lesson=lesson).first()
        if enrollment:
            print(f"✅ User is already enrolled in this lesson (Progress: {enrollment.progress}%)")
        else:
            print(f"ℹ️ User is not enrolled in this lesson. Creating enrollment...")
            enrollment = StudentEnrollment.objects.create(
                student=user,
                lesson=lesson,
                progress=0
            )
            print(f"✅ Created new enrollment")
        
        # Serialize lesson
        lesson_data = LessonSerializer(lesson).data
        print(f"\nLesson data from serializer:")
        for key, value in lesson_data.items():
            print(f"  {key}: {value}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    # Run the test function with default parameters
    test_lesson_access()
    
    # If command line arguments are provided, use them
    if len(sys.argv) > 1:
        lesson_id = int(sys.argv[1])
        user_email = sys.argv[2] if len(sys.argv) > 2 else "rawadalzoubi@gmail.com"
        test_lesson_access(lesson_id, user_email) 