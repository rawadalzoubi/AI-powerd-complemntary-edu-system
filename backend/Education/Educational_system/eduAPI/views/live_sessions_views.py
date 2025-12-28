from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta

from ..models.live_sessions_models import LiveSession, LiveSessionAssignment, LiveSessionMaterial
from ..serializers.live_sessions_serializers import (
    LiveSessionSerializer,
    SessionAssignmentSerializer,
    LiveSessionMaterialSerializer
)


class LiveSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing live sessions"""
    serializer_class = LiveSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter sessions based on user role"""
        user = self.request.user
        
        if user.role == 'TEACHER':
            # Teachers see their own sessions
            return LiveSession.objects.filter(teacher=user).order_by('-scheduled_datetime')
        elif user.role == 'ADVISOR':
            # Advisors see all sessions
            return LiveSession.objects.all().order_by('-scheduled_datetime')
        elif user.role == 'STUDENT':
            # Students see assigned sessions
            return LiveSession.objects.filter(
                assignments__student=user
            ).order_by('-scheduled_datetime')
        else:
            return LiveSession.objects.none()

    def perform_create(self, serializer):
        """Set teacher when creating session"""
        serializer.save(teacher=self.request.user)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending sessions for advisors"""
        if request.user.role != 'ADVISOR':
            return Response(
                {'error': 'Only advisors can view pending sessions'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        sessions = LiveSession.objects.filter(status='PENDING').order_by('-created_at')
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_schedule(self, request):
        """Get user's session schedule"""
        user = request.user
        
        if user.role == 'STUDENT':
            sessions = LiveSession.objects.filter(
                assignments__student=user,
                status__in=['ASSIGNED', 'ACTIVE']
            ).order_by('scheduled_datetime')
        elif user.role == 'TEACHER':
            sessions = LiveSession.objects.filter(
                teacher=user,
                status__in=['ASSIGNED', 'ACTIVE']
            ).order_by('scheduled_datetime')
        else:
            sessions = LiveSession.objects.none()
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign session to students (advisors only)"""
        if request.user.role != 'ADVISOR':
            return Response(
                {'error': 'Only advisors can assign sessions'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        session = self.get_object()
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
                from ..models.user_model import User
                student = User.objects.get(id=student_id, role='STUDENT')
                assignment, created = LiveSessionAssignment.objects.get_or_create(
                    session=session,
                    student=student,
                    defaults={'advisor': request.user, 'assignment_message': message}
                )
                if created:
                    assignments.append(assignment)
            except User.DoesNotExist:
                continue
        
        # Update session status
        if assignments:
            session.status = 'ASSIGNED'
            session.save()
        
        return Response({
            'message': f'Session assigned to {len(assignments)} students',
            'assignments': len(assignments)
        })

    @action(detail=True, methods=['get'])
    def join(self, request, pk=None):
        """Get Jitsi meeting URL for joining session"""
        session = self.get_object()
        user = request.user
        
        # Check if user can join
        if user.role == 'STUDENT':
            # Check if student is assigned
            if not LiveSessionAssignment.objects.filter(session=session, student=user).exists():
                return Response(
                    {'error': 'You are not assigned to this session'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        elif user.role == 'TEACHER':
            # Check if teacher owns the session
            if session.teacher != user:
                return Response(
                    {'error': 'You are not the teacher for this session'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'Invalid user role'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check session timing (allow joining 15 minutes before)
        now = timezone.now()
        session_start = session.scheduled_datetime
        session_end = session_start + timedelta(minutes=session.duration_minutes)
        join_window = session_start - timedelta(minutes=15)
        
        if now < join_window:
            return Response(
                {'error': 'Session has not started yet'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if now > session_end:
            return Response(
                {'error': 'Session has ended'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate Jitsi meeting URL (simplified for now)
        meeting_url = f"https://meet.jit.si/{session.jitsi_room_name}"
        
        # Record join time for students
        if user.role == 'STUDENT':
            assignment = LiveSessionAssignment.objects.get(session=session, student=user)
            if not assignment.join_time:
                assignment.join_time = now
                assignment.save()
        
        return Response({
            'meeting_url': meeting_url,
            'room_name': session.jitsi_room_name,
            'display_name': user.get_full_name(),
            'session_details': self.get_serializer(session).data
        })


class LiveSessionMaterialViewSet(viewsets.ModelViewSet):
    """ViewSet for managing session materials"""
    serializer_class = LiveSessionMaterialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter materials based on user access"""
        user = self.request.user
        session_id = self.request.query_params.get('session')
        
        queryset = LiveSessionMaterial.objects.all()
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        # Filter based on user role
        if user.role == 'STUDENT':
            # Students see materials for their assigned sessions
            queryset = queryset.filter(
                session__assignments__student=user,
                is_public=True
            )
        elif user.role == 'TEACHER':
            # Teachers see materials for their sessions
            queryset = queryset.filter(session__teacher=user)
        elif user.role == 'ADVISOR':
            # Advisors see all materials
            pass
        else:
            queryset = queryset.none()
        
        return queryset.order_by('-uploaded_at')


class CalendarView(APIView):
    """API view for calendar data"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get calendar sessions for the user"""
        user = request.user
        
        # Get date range from query params
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if year and month:
            start_date = datetime(int(year), int(month), 1)
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
        else:
            # Default to current month
            now = timezone.now()
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_date = now.replace(year=now.year + 1, month=1, day=1)
            else:
                end_date = now.replace(month=now.month + 1, day=1)
        
        # Get sessions based on user role
        if user.role == 'STUDENT':
            sessions = LiveSession.objects.filter(
                assignments__student=user,
                scheduled_datetime__gte=start_date,
                scheduled_datetime__lt=end_date
            )
        elif user.role == 'TEACHER':
            sessions = LiveSession.objects.filter(
                teacher=user,
                scheduled_datetime__gte=start_date,
                scheduled_datetime__lt=end_date
            )
        elif user.role == 'ADVISOR':
            sessions = LiveSession.objects.filter(
                scheduled_datetime__gte=start_date,
                scheduled_datetime__lt=end_date
            )
        else:
            sessions = LiveSession.objects.none()
        
        # Format sessions for calendar
        calendar_sessions = []
        for session in sessions:
            calendar_sessions.append({
                'id': session.id,
                'title': session.title,
                'start': session.scheduled_datetime.isoformat(),
                'end': (session.scheduled_datetime + timedelta(minutes=session.duration_minutes)).isoformat(),
                'status': session.status,
                'subject': session.subject,
                'grade_level': session.grade_level,
                'teacher_name': session.teacher.get_full_name() if session.teacher else None,
            })
        
        return Response({
            'sessions': calendar_sessions,
            'metadata': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_sessions': len(calendar_sessions)
            }
        })


class AttendanceReportView(APIView):
    """API view for attendance reports"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get attendance report data"""
        user = request.user
        
        if user.role not in ['TEACHER', 'ADVISOR']:
            return Response(
                {'error': 'Only teachers and advisors can view attendance reports'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get query parameters
        session_id = request.query_params.get('session_id')
        student_id = request.query_params.get('student_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build queryset
        assignments = LiveSessionAssignment.objects.select_related('session', 'student', 'advisor')
        
        if user.role == 'TEACHER':
            assignments = assignments.filter(session__teacher=user)
        
        if session_id:
            assignments = assignments.filter(session_id=session_id)
        
        if student_id:
            assignments = assignments.filter(student_id=student_id)
        
        if date_from:
            assignments = assignments.filter(session__scheduled_datetime__gte=date_from)
        
        if date_to:
            assignments = assignments.filter(session__scheduled_datetime__lte=date_to)
        
        # Calculate attendance statistics
        total_assignments = assignments.count()
        attended_assignments = assignments.filter(attended=True).count()
        attendance_rate = (attended_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        # Serialize assignment data
        from ..serializers.live_sessions_serializers import SessionAssignmentSerializer
        serializer = SessionAssignmentSerializer(assignments, many=True)
        
        return Response({
            'assignments': serializer.data,
            'statistics': {
                'total_assignments': total_assignments,
                'attended_assignments': attended_assignments,
                'attendance_rate': round(attendance_rate, 2)
            }
        })