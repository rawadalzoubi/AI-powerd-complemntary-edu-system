from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import uuid
from datetime import datetime

@api_view(['GET'])
@permission_classes([])  # No authentication required
def test_live_sessions_no_auth(request):
    """Simple test endpoint for live sessions - NO AUTH"""
    return Response({
        'message': 'Live Sessions API is working!',
        'status': 'OK',
        'endpoints': [
            '/api/live-sessions/',
            '/api/live-sessions/my-schedule/',
            '/api/live-sessions/pending/',
        ]
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_live_sessions(request):
    """Simple test endpoint for live sessions"""
    return Response({
        'message': 'Live Sessions API is working!',
        'user': request.user.email,
        'role': getattr(request.user, 'role', 'Unknown')
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_sessions(request):
    """Get/create sessions endpoint using real models"""
    from ..models.live_sessions_models import LiveSession
    
    user = request.user
    
    if request.method == 'POST':
        # Handle session creation
        print(f"DEBUG: User role is: '{user.role}' (type: {type(user.role)})")
        print(f"DEBUG: User: {user}")
        
        # Check role
        if user.role != 'teacher':
            return Response(
                {'error': f'Only teachers can create sessions. Your role is: {user.role}'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        
        # Simple validation
        required_fields = ['title', 'subject', 'level', 'scheduled_datetime']
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'error': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create real session
        try:
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone as django_timezone
            
            # Parse datetime string
            scheduled_dt = data['scheduled_datetime']
            if isinstance(scheduled_dt, str):
                # If it's a string, parse it
                scheduled_dt = parse_datetime(scheduled_dt)
                if not scheduled_dt:
                    # Try alternative parsing
                    from datetime import datetime
                    scheduled_dt = datetime.fromisoformat(scheduled_dt.replace('Z', '+00:00'))
                
                # Make sure it's timezone aware
                if scheduled_dt and not django_timezone.is_aware(scheduled_dt):
                    scheduled_dt = django_timezone.make_aware(scheduled_dt)
            
            session = LiveSession.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                subject=data['subject'],
                level=data['level'],
                scheduled_datetime=scheduled_dt,
                duration_minutes=data.get('duration_minutes', 60),
                max_participants=data.get('max_participants', 50),
                teacher=user,
                jitsi_room_name=f"edutrack-{uuid.uuid4().hex[:8]}"
            )
            
            print(f"DEBUG: Successfully created session {session.id}: {session.title}")
            
            # Verify the session was saved by trying to retrieve it
            try:
                saved_session = LiveSession.objects.get(id=session.id)
                print(f"DEBUG: Verified session exists in database: {saved_session.title}")
            except LiveSession.DoesNotExist:
                print(f"DEBUG: ERROR - Session {session.id} not found in database after creation!")
            return Response({
                'id': session.id,
                'title': session.title,
                'description': session.description,
                'subject': session.subject,
                'level': session.level,
                'status': session.status,
                'scheduled_datetime': session.scheduled_datetime.isoformat(),
                'duration_minutes': session.duration_minutes,
                'teacher_name': user.get_full_name(),
                'can_be_modified': session.can_be_modified,
                'assigned_students_count': 0,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create session: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # GET request - return real data from database
    try:
        print(f"DEBUG: GET sessions for user {user.email} with role {user.role}")
        
        if user.role == 'teacher':
            sessions = LiveSession.objects.filter(teacher=user).order_by('-scheduled_datetime')
            print(f"DEBUG: Found {sessions.count()} sessions for teacher")
        elif user.role == 'advisor':
            sessions = LiveSession.objects.all().order_by('-scheduled_datetime')
            print(f"DEBUG: Found {sessions.count()} total sessions for advisor")
        elif user.role == 'student':
            # Get sessions assigned to this student
            sessions = LiveSession.objects.filter(
                assignments__student=user
            ).order_by('-scheduled_datetime')
            print(f"DEBUG: Found {sessions.count()} assigned sessions for student")
        else:
            sessions = LiveSession.objects.none()
            print(f"DEBUG: Unknown role {user.role}, returning empty queryset")
        
        # Convert to list of dicts
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'title': session.title,
                'description': session.description,
                'subject': session.subject,
                'level': session.level,
                'status': session.status,
                'scheduled_datetime': session.scheduled_datetime.isoformat(),
                'duration_minutes': session.duration_minutes,
                'teacher_name': session.teacher.get_full_name(),
                'can_be_modified': session.can_be_modified,
                'assigned_students_count': session.assignments.count(),
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })
        
        print(f"DEBUG: Returning {len(sessions_data)} sessions")
        return Response(sessions_data)
        
    except Exception as e:
        # Return empty array if database query fails
        print(f"DEBUG: Database query failed: {e}")
        print(f"DEBUG: Returning empty array instead of mock data")
        return Response([])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_schedule(request):
    """Get user's session schedule"""
    user = request.user
    
    try:
        from ..models.live_sessions_models import LiveSession
        
        if user.role == 'student':
            # Get sessions assigned to this student
            sessions = LiveSession.objects.filter(
                assignments__student=user,
                status__in=['ASSIGNED', 'ACTIVE']
            ).order_by('scheduled_datetime')
            print(f"DEBUG: Found {sessions.count()} sessions for student {user.email}")
        elif user.role == 'teacher':
            # Get teacher's upcoming sessions
            sessions = LiveSession.objects.filter(
                teacher=user,
                status__in=['ASSIGNED', 'ACTIVE']
            ).order_by('scheduled_datetime')
            print(f"DEBUG: Found {sessions.count()} sessions for teacher {user.email}")
        else:
            sessions = LiveSession.objects.none()
            print(f"DEBUG: User {user.email} has role {user.role}, no sessions returned")
        
        # Convert to list of dicts
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'title': session.title,
                'description': session.description,
                'subject': session.subject,
                'level': session.level,
                'status': session.status,
                'scheduled_datetime': session.scheduled_datetime.isoformat(),
                'duration_minutes': session.duration_minutes,
                'teacher_name': session.teacher.get_full_name(),
                'can_be_modified': session.can_be_modified,
                'assigned_students_count': session.assignments.count(),
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })
        
        return Response(sessions_data)
        
    except Exception as e:
        print(f"Error in get_my_schedule: {e}")
        # Return empty list if database is not available
        # This way students will see "No sessions assigned" instead of mock data
        return Response([])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_sessions(request):
    """Get pending sessions for advisors"""
    user = request.user
    
    if user.role == 'ADVISOR':
        mock_sessions = [
            {
                'id': 4,
                'title': 'Chemistry - Organic Compounds',
                'description': 'Introduction to organic chemistry',
                'subject': 'Chemistry',
                'level': '11',
                'status': 'PENDING',
                'scheduled_datetime': '2024-12-22T11:00:00Z',
                'duration_minutes': 60,
                'teacher_name': 'Dr. Ahmed Hassan'
            }
        ]
    else:
        mock_sessions = []
    
    return Response(mock_sessions)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_session(request, session_id):
    """Assign session to students (advisors only)"""
    user = request.user
    
    # Check if user is advisor
    if user.role != 'advisor':
        return Response(
            {'error': 'Only advisors can assign sessions'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from ..models.live_sessions_models import LiveSession, LiveSessionAssignment
        from ..models.user_model import User
        
        # Get the session
        session = LiveSession.objects.get(id=session_id)
        
        # Get data from request
        student_ids = request.data.get('student_ids', [])
        message = request.data.get('message', '')
        
        if not student_ids:
            return Response(
                {'error': 'No students selected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create assignments
        assignments = []
        for student_id in student_ids:
            try:
                student = User.objects.get(id=student_id, role='student')
                assignment, created = LiveSessionAssignment.objects.get_or_create(
                    session=session,
                    student=student,
                    defaults={'advisor': user, 'assignment_message': message}
                )
                if created:
                    assignments.append(assignment)
                    print(f"DEBUG: Created assignment for student {student.email} to session {session.title}")
                else:
                    print(f"DEBUG: Assignment already exists for student {student.email} to session {session.title}")
            except User.DoesNotExist:
                print(f"DEBUG: Student with id {student_id} not found")
                continue
        
        # Update session status
        if assignments:
            session.status = 'ASSIGNED'
            session.save()
            print(f"DEBUG: Updated session {session.title} status to ASSIGNED")
        
        print(f"DEBUG: Total assignments created: {len(assignments)}")
        return Response({
            'message': f'Session assigned to {len(assignments)} students',
            'assignments': len(assignments),
            'session_id': session.id,
            'session_status': session.status
        })
        
    except LiveSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to assign session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_session(request, session_id):
    """Update session (teachers only)"""
    user = request.user
    
    # Check if user is teacher
    if user.role != 'teacher':
        return Response(
            {'error': 'Only teachers can update sessions'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from ..models.live_sessions_models import LiveSession
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone as django_timezone
        
        # Get the session
        session = LiveSession.objects.get(id=session_id, teacher=user)
        
        # Check if session can be modified
        if not session.can_be_modified:
            return Response(
                {'error': 'Session cannot be modified'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data
        
        # Update fields
        if 'title' in data:
            session.title = data['title']
        if 'description' in data:
            session.description = data['description']
        if 'subject' in data:
            session.subject = data['subject']
        if 'level' in data:
            session.level = data['level']
        if 'duration_minutes' in data:
            session.duration_minutes = data['duration_minutes']
        if 'max_participants' in data:
            session.max_participants = data['max_participants']
        
        # Update scheduled datetime if provided
        if 'scheduled_datetime' in data:
            scheduled_dt = data['scheduled_datetime']
            if isinstance(scheduled_dt, str):
                scheduled_dt = parse_datetime(scheduled_dt)
                if not scheduled_dt:
                    from datetime import datetime
                    scheduled_dt = datetime.fromisoformat(scheduled_dt.replace('Z', '+00:00'))
                
                if scheduled_dt and not django_timezone.is_aware(scheduled_dt):
                    scheduled_dt = django_timezone.make_aware(scheduled_dt)
            
            session.scheduled_datetime = scheduled_dt
        
        session.save()
        
        return Response({
            'id': session.id,
            'title': session.title,
            'description': session.description,
            'subject': session.subject,
            'level': session.level,
            'status': session.status,
            'scheduled_datetime': session.scheduled_datetime.isoformat(),
            'duration_minutes': session.duration_minutes,
            'teacher_name': user.get_full_name(),
            'can_be_modified': session.can_be_modified,
            'assigned_students_count': session.assignments.count(),
            'updated_at': session.updated_at.isoformat()
        })
        
    except LiveSession.DoesNotExist:
        return Response(
            {'error': 'Session not found or you do not have permission to update it'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to update session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_session(request, session_id):
    """Cancel session (teachers only)"""
    user = request.user
    
    # Check if user is teacher
    if user.role != 'teacher':
        return Response(
            {'error': 'Only teachers can cancel sessions'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from ..models.live_sessions_models import LiveSession
        
        # Get the session
        session = LiveSession.objects.get(id=session_id, teacher=user)
        
        # Check if session can be cancelled (only PENDING sessions)
        if session.status not in ['PENDING', 'ASSIGNED']:
            return Response(
                {'error': 'Only pending or assigned sessions can be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status to cancelled
        session.status = 'CANCELLED'
        session.save()
        
        return Response({
            'message': f'Session "{session.title}" has been cancelled',
            'session_id': session.id
        })
        
    except LiveSession.DoesNotExist:
        return Response(
            {'error': 'Session not found or you do not have permission to cancel it'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to cancel session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_session(request, session_id):
    """Assign session to students (advisors only)"""
    user = request.user
    
    # Check if user is advisor
    if user.role != 'advisor':
        return Response(
            {'error': 'Only advisors can assign sessions'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from ..models.live_sessions_models import LiveSession, LiveSessionAssignment
        from ..models.user_model import User
        
        # Get the session
        session = LiveSession.objects.get(id=session_id)
        
        # Get data from request
        student_ids = request.data.get('student_ids', [])
        message = request.data.get('message', '')
        
        if not student_ids:
            return Response(
                {'error': 'No students selected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create assignments (allow multiple assignments)
        assignments = []
        existing_assignments = []
        
        for student_id in student_ids:
            try:
                student = User.objects.get(id=student_id, role='student')
                
                # Check if assignment already exists
                existing_assignment = LiveSessionAssignment.objects.filter(
                    session=session,
                    student=student
                ).first()
                
                if existing_assignment:
                    existing_assignments.append(student.get_full_name())
                    print(f"DEBUG: Assignment already exists for student {student.email}")
                else:
                    # Create new assignment
                    assignment = LiveSessionAssignment.objects.create(
                        session=session,
                        student=student,
                        advisor=user,
                        assignment_message=message
                    )
                    assignments.append(assignment)
                    print(f"DEBUG: Created new assignment for student {student.email}")
                    
            except User.DoesNotExist:
                print(f"DEBUG: Student with id {student_id} not found")
                continue
        
        # Update session status if new assignments were created
        if assignments:
            session.status = 'ASSIGNED'
            session.save()
            print(f"DEBUG: Updated session {session.title} status to ASSIGNED")
        
        response_message = f'Session assigned to {len(assignments)} new students'
        if existing_assignments:
            response_message += f'. {len(existing_assignments)} students were already assigned'
        
        print(f"DEBUG: Total new assignments created: {len(assignments)}")
        return Response({
            'message': response_message,
            'new_assignments': len(assignments),
            'existing_assignments': len(existing_assignments),
            'session_id': session.id,
            'session_status': session.status
        })
        
    except LiveSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to assign session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assigned_students(request, session_id):
    """Get students assigned to a session (advisors only)"""
    user = request.user
    
    print(f"DEBUG: get_assigned_students called with session_id: {session_id}")
    print(f"DEBUG: User: {user.email}, Role: {user.role}")
    
    # Check if user is advisor
    if user.role != 'advisor':
        print(f"DEBUG: User is not advisor, role is: {user.role}")
        return Response(
            {'error': 'Only advisors can view assigned students'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from ..models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        print(f"DEBUG: Looking for session with ID: {session_id}")
        
        # Get the session
        session = LiveSession.objects.get(id=session_id)
        print(f"DEBUG: Found session: {session.title}")
        
        # Get all assignments for this session
        assignments = LiveSessionAssignment.objects.filter(session=session).select_related('student')
        print(f"DEBUG: Found {assignments.count()} assignments for this session")
        
        # Convert to list of student data
        students_data = []
        for assignment in assignments:
            student = assignment.student
            students_data.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'grade_level': getattr(student, 'grade_level', None),
                'assignment_date': assignment.assigned_date.isoformat(),
                'join_time': assignment.join_time.isoformat() if assignment.join_time else None
            })
        
        print(f"DEBUG: Returning {len(students_data)} students")
        return Response({
            'session_id': session.id,
            'session_title': session.title,
            'students': students_data,
            'total_assigned': len(students_data)
        })
        
    except LiveSession.DoesNotExist:
        print(f"DEBUG: Session with ID {session_id} not found in database")
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"DEBUG: Exception in get_assigned_students: {str(e)}")
        return Response(
            {'error': f'Failed to get assigned students: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([])  # No auth required for debugging
def debug_sessions(request):
    """Debug endpoint to see all sessions in database"""
    try:
        from ..models.live_sessions_models import LiveSession
        
        sessions = LiveSession.objects.all()
        sessions_data = []
        
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'title': session.title,
                'status': session.status,
                'teacher': session.teacher.email if session.teacher else 'No teacher',
                'created_at': session.created_at.isoformat(),
                'assigned_count': session.assignments.count()
            })
        
        return Response({
            'total_sessions': len(sessions_data),
            'sessions': sessions_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Debug failed: {str(e)}',
            'sessions': []
        })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unassign_session(request, session_id):
    """Unassign students from session (advisors only)"""
    user = request.user
    
    # Check if user is advisor
    if user.role != 'advisor':
        return Response(
            {'error': 'Only advisors can unassign sessions'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from ..models.live_sessions_models import LiveSession, LiveSessionAssignment
        
        # Get the session
        session = LiveSession.objects.get(id=session_id)
        
        # Get student IDs to unassign
        student_ids = request.data.get('student_ids', [])
        
        if not student_ids:
            return Response(
                {'error': 'No students selected for unassignment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove assignments
        removed_count = 0
        removed_students = []
        for student_id in student_ids:
            try:
                assignment = LiveSessionAssignment.objects.get(
                    session=session,
                    student_id=student_id
                )
                student_name = assignment.student.get_full_name()
                assignment.delete()
                removed_count += 1
                removed_students.append(student_name)
                print(f"DEBUG: Removed assignment for student {student_name}")
            except LiveSessionAssignment.DoesNotExist:
                print(f"DEBUG: No assignment found for student {student_id}")
                continue
        
        # Update session status if no assignments left
        remaining_assignments = LiveSessionAssignment.objects.filter(session=session).count()
        if remaining_assignments == 0:
            session.status = 'PENDING'
            session.save()
            print(f"DEBUG: Updated session status to PENDING (no assignments left)")
        
        return Response({
            'message': f'تم إلغاء إسناد {removed_count} طلاب من الجلسة',
            'removed_assignments': removed_count,
            'remaining_assignments': remaining_assignments,
            'removed_students': removed_students,
            'session_status': session.status
        })
        
    except LiveSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to unassign session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def join_session(request, session_id):
    """Join a live session"""
    user = request.user
    
    try:
        from ..models.live_sessions_models import LiveSession, LiveSessionAssignment
        from django.utils import timezone
        from datetime import timedelta
        
        print(f"DEBUG: User {user.email} trying to join session {session_id}")
        
        # Get the session
        try:
            session = LiveSession.objects.get(id=session_id)
            print(f"DEBUG: Found session: {session.title}")
        except LiveSession.DoesNotExist:
            print(f"DEBUG: Session {session_id} not found")
            return Response(
                {'error': 'Session not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user can join
        can_join = False
        if user.role == 'student':
            # Check if student is assigned to this session
            try:
                assignment = LiveSessionAssignment.objects.get(session=session, student=user)
                can_join = True
                print(f"DEBUG: Student is assigned to session")
                
                # Record join time (update each time student joins)
                assignment.join_time = timezone.now()
                assignment.save()
                print(f"DEBUG: Updated join time for student (allows re-joining)")
                    
            except LiveSessionAssignment.DoesNotExist:
                print(f"DEBUG: Student is not assigned to this session")
                return Response(
                    {'error': 'You are not assigned to this session'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
        elif user.role == 'teacher':
            # Check if teacher owns the session
            if session.teacher == user:
                can_join = True
                print(f"DEBUG: Teacher owns the session")
            else:
                print(f"DEBUG: Teacher does not own this session")
                return Response(
                    {'error': 'You are not the teacher for this session'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        elif user.role == 'advisor':
            print(f"DEBUG: Advisor cannot join sessions - role is for management only")
            return Response(
                {'error': 'Advisors cannot join sessions. Your role is to assign sessions to students.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            print(f"DEBUG: Invalid user role: {user.role}")
            return Response(
                {'error': 'Invalid user role for joining sessions'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check session timing with new rules
        now = timezone.now()
        session_start = session.scheduled_datetime
        session_end = session_start + timedelta(minutes=session.duration_minutes)
        
        print(f"DEBUG: Current time: {now}")
        print(f"DEBUG: Session start: {session_start}")
        print(f"DEBUG: Session end: {session_end}")
        print(f"DEBUG: User role: {user.role}")
        print(f"DEBUG: Session status: {session.status}")
        
        if user.role == 'teacher':
            # Teachers can join their sessions if:
            # 1. Session is not CANCELLED
            # 2. Session has not ended yet
            if session.status == 'CANCELLED':
                return Response(
                    {'error': 'This session has been cancelled'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if now > session_end:
                return Response(
                    {'error': 'Session has ended and is no longer accessible'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Allow teachers to join 15 minutes before session starts
            join_window = session_start - timedelta(minutes=15)
            if now < join_window:
                minutes_until = max(1, int((join_window - now).total_seconds() / 60))
                return Response(
                    {'error': f'You can join this session in {minutes_until} minutes (15 minutes before start time)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        elif user.role == 'student':
            # Students can join if:
            # 1. Session is ASSIGNED or ACTIVE
            # 2. Within the first 10 minutes of the session (late join window)
            # 3. Can leave and re-join multiple times within this window
            if session.status not in ['ASSIGNED', 'ACTIVE']:
                return Response(
                    {'error': 'This session is not available for joining'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Students can join from session start until 10 minutes after start
            # They can leave and re-join multiple times within this window
            late_join_window = session_start + timedelta(minutes=10)
            
            if now < session_start:
                minutes_until = max(1, int((session_start - now).total_seconds() / 60))
                return Response(
                    {'error': f'Session starts in {minutes_until} minutes. Please wait.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if now > late_join_window:
                return Response(
                    {'error': 'Late join period has ended. You can only join within the first 10 minutes of the session.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"DEBUG: Student can join - within late join window (first 10 minutes, re-joining allowed)")
        
        print(f"DEBUG: Join allowed for {user.role}")
        
        # Generate Jitsi meeting URL
        meeting_url = f"https://meet.jit.si/{session.jitsi_room_name}"
        
        print(f"DEBUG: Generated meeting URL: {meeting_url}")
        
        # Add helpful message for students about re-joining
        response_data = {
            'meeting_url': meeting_url,
            'room_name': session.jitsi_room_name,
            'display_name': user.get_full_name(),
            'session_details': {
                'id': session.id,
                'title': session.title,
                'status': session.status,
                'teacher_name': session.teacher.get_full_name(),
                'scheduled_datetime': session.scheduled_datetime.isoformat(),
                'duration_minutes': session.duration_minutes
            }
        }
        
        # Add re-join message for students
        if user.role == 'student':
            late_join_window = session_start + timedelta(minutes=10)
            minutes_left = max(0, int((late_join_window - now).total_seconds() / 60))
            response_data['message'] = f"You can leave and re-join this session for the next {minutes_left} minutes."
        
        return Response(response_data)
        
    except Exception as e:
        print(f"DEBUG: Error in join_session: {str(e)}")
        # Fallback to simple URL generation
        meeting_url = f"https://meet.jit.si/edutrack-session-{session_id}"
        
        return Response({
            'meeting_url': meeting_url,
            'room_name': f'edutrack-session-{session_id}',
            'display_name': user.get_full_name(),
            'session_details': {
                'id': session_id,
                'title': 'Session',
                'status': 'ACTIVE'
            }
        })