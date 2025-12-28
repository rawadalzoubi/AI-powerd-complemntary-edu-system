# backend/Education/Educational_syste_views.pyive_sessionsPI/views/lm/eduA
# Live Sessions Views - Following existing codebase patterns

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from ..models.live_sessions_model import (
    LiveSession, 
    LiveSessionAssignment, 
    LiveSessionMaterial,
    LiveSessionNotification
)
from ..serializers.live_sessions_serializers import (
    LiveSessionSerializer,
    LiveSessionDetailSerializer,
    LiveSessionAssignmentSerializer,
    LiveSessionMaterialSerializer
)


class LiveSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing live sessions.
    Following existing viewset patterns in the codebase.
    """
    
    serializer_class = LiveSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter sessions based on user role"""
        user = self.request.user
        
        if user.user_type == 'TEACHER':
            return LiveSession.objects.filter(teacher=user)
        elif user.user_type == 'ADVISOR':
            # Advisors can see all sessions for assignment
            return LiveSession.objects.all()
        elif user.user_type == 'STUDENT':
            # Students see only assigned sessions
            return LiveSession.objects.filter(
                assignments__student=user
            ).distinct()
        else:
            return LiveSession.objects.none()
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return LiveSessionDetailSerializer
        return LiveSessionSerializer
    
    def perform_create(self, serializer):
        """Set teacher as current user when creating session"""
        if self.request.user.user_type != 'TEACHER':
            raise permissions.PermissionDenied("Only teachers can create sessions")
        
        # Generate unique Jitsi room name
        import uuid
        room_name = f"edutrack-{uuid.uuid4().hex[:8]}-{int(timezone.now().timestamp())}"
        
        serializer.save(
            teacher=self.request.user,
            jitsi_room_name=room_name
        )
    
    def update(self, request, *args, **kwargs):
        """Allow updates only for pending sessions by teachers"""
        session = self.get_object()
        
        if request.user != session.teacher:
            return Response(
                {"error": "Only the session teacher can update this session"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not session.can_be_modified:
            return Response(
                {"error": "Cannot modify session that is already assigned or active"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Cancel session instead of deleting"""
        session = self.get_object()
        
        if request.user != session.teacher:
            return Response(
                {"error": "Only the session teacher can cancel this session"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if session.status == 'ACTIVE':
            return Response(
                {"error": "Cannot cancel an active session"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel session and notify assigned students
        session.status = 'CANCELLED'
        session.save()
        
        # TODO: Send cancellation notifications
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending sessions for advisors"""
        if request.user.user_type != 'ADVISOR':
            return Response(
                {"error": "Only advisors can view pending sessions"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        sessions = LiveSession.objects.filter(status='PENDING')
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_schedule(self, request):
        """Get user's session schedule"""
        user = request.user
        
        if user.user_type == 'STUDENT':
            sessions = LiveSession.objects.filter(
                assignments__student=user
            ).distinct()
        elif user.user_type == 'TEACHER':
            sessions = LiveSession.objects.filter(teacher=user)
        elif user.user_type == 'ADVISOR':
            sessions = LiveSession.objects.filter(
                assignments__advisor=user
            ).distinct()
        else:
            sessions = LiveSession.objects.none()
        
        # Filter by date range if provided
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            sessions = sessions.filter(scheduled_datetime__gte=date_from)
        if date_to:
            sessions = sessions.filter(scheduled_datetime__lte=date_to)
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign session to students (Advisors only)"""
        if request.user.user_type != 'ADVISOR':
            return Response(
                {"error": "Only advisors can assign sessions"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session = self.get_object()
        
        if session.status != 'PENDING':
            return Response(
                {"error": "Can only assign pending sessions"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student_ids = request.data.get('student_ids', [])
        message = request.data.get('message', '')
        
        if not student_ids:
            return Response(
                {"error": "At least one student must be selected"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create assignments
        assignments = []
        for student_id in student_ids:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                student = User.objects.get(id=student_id, user_type='STUDENT')
                
                assignment, created = LiveSessionAssignment.objects.get_or_create(
                    session=session,
                    student=student,
                    defaults={
                        'advisor': request.user,
                        'assignment_message': message
                    }
                )
                
                if created:
                    assignments.append(assignment)
                    # TODO: Send assignment notification
                
            except User.DoesNotExist:
                continue
        
        if assignments:
            session.status = 'ASSIGNED'
            session.save()
        
        return Response({
            "message": f"Session assigned to {len(assignments)} students",
            "assignments": len(assignments)
        })
    
    @action(detail=True, methods=['get'])
    def join(self, request, pk=None):
        """Get Jitsi meeting URL for students"""
        session = self.get_object()
        user = request.user
        
        if user.user_type != 'STUDENT':
            # Teachers can also join as moderators
            if user.user_type == 'TEACHER' and user == session.teacher:
                is_moderator = True
            else:
                return Response(
                    {"error": "Only assigned students and teachers can join sessions"},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            # Check if student is assigned
            try:
                assignment = LiveSessionAssignment.objects.get(
                    session=session,
                    student=user
                )
                is_moderator = False
            except LiveSessionAssignment.DoesNotExist:
                return Response(
                    {"error": "You are not assigned to this session"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check session timing
        if not session.is_active and session.status != 'ASSIGNED':
            return Response(
                {"error": "Session is not active"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate Jitsi meeting URL
        meeting_url = f"https://meet.jit.si/{session.jitsi_room_name}"
        
        # Record join time for students
        if user.user_type == 'STUDENT':
            assignment.join_time = timezone.now()
            assignment.attended = True
            assignment.save()
        
        return Response({
            "meeting_url": meeting_url,
            "room_name": session.jitsi_room_name,
            "display_name": user.get_full_name(),
            "is_moderator": is_moderator,
            "session_details": LiveSessionDetailSerializer(session).data
        })


class LiveSessionMaterialViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing session materials.
    Following existing material management patterns.
    """
    
    serializer_class = LiveSessionMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter materials based on user access"""
        user = self.request.user
        
        if user.user_type == 'TEACHER':
            # Teachers see materials for their sessions
            return LiveSessionMaterial.objects.filter(session__teacher=user)
        elif user.user_type in ['STUDENT', 'ADVISOR']:
            # Students and advisors see public materials for assigned sessions
            return LiveSessionMaterial.objects.filter(
                is_public=True,
                session__assignments__student=user
            ).distinct()
        else:
            return LiveSessionMaterial.objects.none()
    
    def perform_create(self, serializer):
        """Set uploader as current user"""
        serializer.save(uploaded_by=self.request.user)


class CalendarView(APIView):
    """
    Calendar view for sessions.
    Following existing API view patterns.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get calendar data for user"""
        user = request.user
        
        # Get date range parameters
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        view_type = request.query_params.get('view', 'month')
        
        # Build base queryset based on user role
        if user.user_type == 'STUDENT':
            sessions = LiveSession.objects.filter(
                assignments__student=user
            ).distinct()
        elif user.user_type == 'TEACHER':
            sessions = LiveSession.objects.filter(teacher=user)
        elif user.user_type == 'ADVISOR':
            sessions = LiveSession.objects.filter(
                assignments__advisor=user
            ).distinct()
        else:
            sessions = LiveSession.objects.none()
        
        # Apply date filters
        if year and month:
            sessions = sessions.filter(
                scheduled_datetime__year=year,
                scheduled_datetime__month=month
            )
        
        # Serialize sessions for calendar
        calendar_data = []
        for session in sessions:
            calendar_data.append({
                'id': session.id,
                'title': session.title,
                'start': session.scheduled_datetime.isoformat(),
                'end': (session.scheduled_datetime + timedelta(minutes=session.duration_minutes)).isoformat(),
                'status': session.status,
                'subject': session.subject,
                'teacher': session.teacher.get_full_name(),
                'can_join': session.is_active and user.user_type in ['STUDENT', 'TEACHER']
            })
        
        return Response({
            'sessions': calendar_data,
            'view': view_type,
            'year': year,
            'month': month
        })


class AttendanceReportView(APIView):
    """
    Attendance reports for advisors and teachers.
    Following existing reporting patterns.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Generate attendance report"""
        user = request.user
        
        if user.user_type not in ['TEACHER', 'ADVISOR']:
            return Response(
                {"error": "Only teachers and advisors can view attendance reports"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get filter parameters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        student_id = request.query_params.get('student_id')
        session_id = request.query_params.get('session_id')
        
        # Build queryset
        assignments = LiveSessionAssignment.objects.select_related(
            'session', 'student', 'advisor'
        )
        
        if user.user_type == 'TEACHER':
            assignments = assignments.filter(session__teacher=user)
        elif user.user_type == 'ADVISOR':
            assignments = assignments.filter(advisor=user)
        
        # Apply filters
        if date_from:
            assignments = assignments.filter(session__scheduled_datetime__gte=date_from)
        if date_to:
            assignments = assignments.filter(session__scheduled_datetime__lte=date_to)
        if student_id:
            assignments = assignments.filter(student_id=student_id)
        if session_id:
            assignments = assignments.filter(session_id=session_id)
        
        # Calculate statistics
        total_assignments = assignments.count()
        attended_assignments = assignments.filter(attended=True).count()
        attendance_rate = (attended_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        # Serialize assignment data
        assignment_data = []
        for assignment in assignments:
            assignment_data.append({
                'session_title': assignment.session.title,
                'student_name': assignment.student.get_full_name(),
                'scheduled_datetime': assignment.session.scheduled_datetime.isoformat(),
                'attended': assignment.attended,
                'join_time': assignment.join_time.isoformat() if assignment.join_time else None,
                'leave_time': assignment.leave_time.isoformat() if assignment.leave_time else None,
                'attendance_percentage': assignment.attendance_percentage,
                'duration_minutes': assignment.attendance_duration_minutes
            })
        
        return Response({
            'assignments': assignment_data,
            'statistics': {
                'total_assignments': total_assignments,
                'attended_assignments': attended_assignments,
                'attendance_rate': round(attendance_rate, 2)
            }
        })