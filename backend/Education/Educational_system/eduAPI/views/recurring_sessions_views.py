# backend/Education/Educational_system/eduAPI/views/recurring_sessions_views.py
# Views for recurring sessions functionality

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from ..models.recurring_sessions_models import (
    SessionTemplate,
    StudentGroup,
    TemplateGroupAssignment,
    GeneratedSession,
    TemplateGenerationLog
)
from ..serializers.recurring_sessions_serializers import (
    SessionTemplateSerializer,
    StudentGroupSerializer,
    TemplateGroupAssignmentSerializer,
    GeneratedSessionSerializer,
    TemplateGenerationLogSerializer,
    SessionTemplateSimpleSerializer,
    StudentGroupSimpleSerializer,
    StudentSimpleSerializer
)


class SessionTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing session templates"""
    
    serializer_class = SessionTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter templates based on user role"""
        user = self.request.user
        
        print(f"DEBUG: User {user.email} with role {user.role} accessing templates")
        
        if user.role == 'teacher':
            # Teachers see only their own templates
            queryset = SessionTemplate.objects.filter(teacher=user)
            print(f"DEBUG: Teacher queryset count: {queryset.count()}")
            return queryset
        elif user.role == 'advisor':
            # Advisors see all templates for assignment purposes
            queryset = SessionTemplate.objects.all()
            print(f"DEBUG: Advisor queryset count: {queryset.count()}")
            return queryset
        else:
            # Students don't manage templates
            print(f"DEBUG: Student/other role - returning empty queryset")
            return SessionTemplate.objects.none()
    
    def perform_create(self, serializer):
        """Set the teacher to current user"""
        serializer.save(teacher=self.request.user)
    
    def perform_update(self, serializer):
        """Only allow teachers to update their own templates"""
        if self.request.user != serializer.instance.teacher:
            raise permissions.PermissionDenied("You can only update your own templates")
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a template"""
        template = self.get_object()
        if request.user != template.teacher:
            return Response(
                {'error': 'You can only pause your own templates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        template.status = 'PAUSED'
        template.save()
        
        return Response({
            'message': f'Template "{template.title}" has been paused',
            'status': template.status
        })
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused template"""
        template = self.get_object()
        if request.user != template.teacher:
            return Response(
                {'error': 'You can only resume your own templates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        template.status = 'ACTIVE'
        template.save()
        
        return Response({
            'message': f'Template "{template.title}" has been resumed',
            'status': template.status
        })
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a template permanently"""
        template = self.get_object()
        if request.user != template.teacher:
            return Response(
                {'error': 'You can only end your own templates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        template.status = 'ENDED'
        template.save()
        
        return Response({
            'message': f'Template "{template.title}" has been ended',
            'status': template.status
        })
    
    @action(detail=True, methods=['get'])
    def generated_sessions(self, request, pk=None):
        """Get sessions generated from this template"""
        template = self.get_object()
        generated_sessions = GeneratedSession.objects.filter(template=template)
        serializer = GeneratedSessionSerializer(generated_sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def assignments(self, request, pk=None):
        """Get or create assignments for this template"""
        template = self.get_object()
        
        if request.method == 'GET':
            # Get existing assignments
            assignments = TemplateGroupAssignment.objects.filter(
                template=template, 
                is_active=True
            )
            serializer = TemplateGroupAssignmentSerializer(assignments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Create new assignments for students
            try:
                print(f"DEBUG: POST assignments called by {request.user.email}")
                print(f"DEBUG: Request data: {request.data}")
                
                if request.user.role != 'advisor':
                    return Response(
                        {'error': 'Only advisors can assign templates'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                student_ids = request.data.get('student_ids', [])
                print(f"DEBUG: Student IDs: {student_ids}")
                
                if not student_ids:
                    return Response(
                        {'error': 'No students provided'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # For now, create individual assignments for each student
                from ..models.user_model import User
                assigned_count = 0
                
                for student_id in student_ids:
                    try:
                        print(f"DEBUG: Processing student ID: {student_id}")
                        student = User.objects.get(id=student_id, role='student')
                        print(f"DEBUG: Found student: {student.first_name} {student.last_name}")
                        
                        # Create or get a group for this student (individual group)
                        group_name = f"Individual - {student.first_name} {student.last_name}"
                        group, group_created = StudentGroup.objects.get_or_create(
                            name=group_name,
                            advisor=request.user,
                            defaults={
                                'description': f'Individual group for {student.first_name} {student.last_name}',
                                'is_active': True
                            }
                        )
                        print(f"DEBUG: Group {'created' if group_created else 'found'}: {group.name}")
                        
                        # Add student to group if not already there
                        if not group.students.filter(id=student.id).exists():
                            group.students.add(student)
                            print(f"DEBUG: Added student to group")
                        
                        # Check if assignment already exists
                        existing_assignment = TemplateGroupAssignment.objects.filter(
                            template=template,
                            group=group,
                            advisor=request.user
                        ).first()
                        
                        if existing_assignment:
                            if not existing_assignment.is_active:
                                existing_assignment.is_active = True
                                existing_assignment.save()
                                print(f"DEBUG: Reactivated existing assignment")
                                assigned_count += 1
                            else:
                                print(f"DEBUG: Assignment already exists and is active")
                        else:
                            # Create new assignment
                            assignment = TemplateGroupAssignment.objects.create(
                                template=template,
                                group=group,
                                advisor=request.user,
                                is_active=True,
                                assignment_message=f'Assigned to {student.first_name} {student.last_name}'
                            )
                            print(f"DEBUG: Created new assignment {assignment.id}")
                            assigned_count += 1
                            
                    except User.DoesNotExist:
                        print(f"DEBUG: Student {student_id} not found")
                        continue
                    except Exception as e:
                        print(f"DEBUG: Error processing student {student_id}: {str(e)}")
                        continue
                
                print(f"DEBUG: Successfully assigned to {assigned_count} students")
                return Response({
                    'message': f'Template assigned to {assigned_count} students',
                    'assigned_count': assigned_count
                })
                
            except Exception as e:
                print(f"DEBUG: Major error in assignments POST: {str(e)}")
                import traceback
                traceback.print_exc()
                return Response(
                    {'error': f'Internal server error: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=True, methods=['get'])
    def assigned_students(self, request, pk=None):
        """Get list of students assigned to this template"""
        template = self.get_object()
        
        # Get all active assignments for this template
        assignments = TemplateGroupAssignment.objects.filter(
            template=template,
            is_active=True
        )
        
        # Collect all students from assigned groups
        students = []
        seen_student_ids = set()
        
        for assignment in assignments:
            for student in assignment.group.students.all():
                if student.id not in seen_student_ids:
                    students.append({
                        'id': student.id,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'email': student.email,
                        'full_name': student.get_full_name()
                    })
                    seen_student_ids.add(student.id)
        
        return Response(students)
    
    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Unassign students from template"""
        template = self.get_object()
        
        if request.user.role != 'advisor':
            return Response(
                {'error': 'Only advisors can unassign templates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        student_ids = request.data.get('student_ids', [])
        
        if not student_ids:
            return Response(
                {'error': 'No students provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from ..models.user_model import User
        unassigned_count = 0
        
        for student_id in student_ids:
            try:
                student = User.objects.get(id=student_id, role='student')
                
                # Find the individual group for this student
                group_name = f"Individual - {student.first_name} {student.last_name}"
                group = StudentGroup.objects.filter(
                    name=group_name,
                    advisor=request.user
                ).first()
                
                if group:
                    # Find and deactivate the assignment
                    assignment = TemplateGroupAssignment.objects.filter(
                        template=template,
                        group=group,
                        advisor=request.user,
                        is_active=True
                    ).first()
                    
                    if assignment:
                        assignment.is_active = False
                        assignment.save()
                        unassigned_count += 1
                        print(f"DEBUG: Unassigned student {student.id} from template {template.id}")
                    
            except User.DoesNotExist:
                print(f"DEBUG: Student {student_id} not found")
                continue
        
        return Response({
            'message': f'Unassigned {unassigned_count} students from template',
            'unassigned_count': unassigned_count
        })
    
    @action(detail=False, methods=['get'])
    def simple(self, request):
        """Get simplified template list for dropdowns"""
        templates = self.get_queryset().filter(status='ACTIVE')
        serializer = SessionTemplateSimpleSerializer(templates, many=True)
        return Response(serializer.data)


class StudentGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student groups"""
    
    serializer_class = StudentGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter groups based on user role"""
        user = self.request.user
        
        if user.role == 'advisor':
            # Advisors see only their own groups
            return StudentGroup.objects.filter(advisor=user)
        else:
            # Only advisors can manage groups
            return StudentGroup.objects.none()
    
    def perform_create(self, serializer):
        """Set the advisor to current user"""
        serializer.save(advisor=self.request.user)
    
    def perform_update(self, serializer):
        """Only allow advisors to update their own groups"""
        if self.request.user != serializer.instance.advisor:
            raise permissions.PermissionDenied("You can only update your own groups")
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def add_students(self, request, pk=None):
        """Add students to a group"""
        group = self.get_object()
        student_ids = request.data.get('student_ids', [])
        
        added_count = 0
        for student_id in student_ids:
            try:
                from ..models.user_model import User
                student = User.objects.get(id=student_id, role='student')
                group.students.add(student)
                added_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'message': f'Added {added_count} students to group "{group.name}"',
            'total_students': group.student_count
        })
    
    @action(detail=True, methods=['post'])
    def remove_students(self, request, pk=None):
        """Remove students from a group"""
        group = self.get_object()
        student_ids = request.data.get('student_ids', [])
        
        removed_count = 0
        for student_id in student_ids:
            try:
                from ..models.user_model import User
                student = User.objects.get(id=student_id)
                group.students.remove(student)
                removed_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'message': f'Removed {removed_count} students from group "{group.name}"',
            'total_students': group.student_count
        })
    
    @action(detail=True, methods=['get'])
    def template_assignments(self, request, pk=None):
        """Get template assignments for this group"""
        group = self.get_object()
        assignments = TemplateGroupAssignment.objects.filter(
            group=group, 
            is_active=True
        )
        serializer = TemplateGroupAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def simple(self, request):
        """Get simplified group list for dropdowns"""
        groups = self.get_queryset().filter(is_active=True)
        serializer = StudentGroupSimpleSerializer(groups, many=True)
        return Response(serializer.data)


class TemplateGroupAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing template-group assignments"""
    
    serializer_class = TemplateGroupAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter assignments based on user role"""
        user = self.request.user
        
        if user.role == 'advisor':
            # Advisors see only their own assignments
            return TemplateGroupAssignment.objects.filter(advisor=user)
        elif user.role == 'teacher':
            # Teachers see assignments to their templates
            return TemplateGroupAssignment.objects.filter(template__teacher=user)
        else:
            return TemplateGroupAssignment.objects.none()
    
    def perform_create(self, serializer):
        """Set the advisor to current user and validate permissions"""
        group = serializer.validated_data['group']
        if group.advisor != self.request.user:
            raise permissions.PermissionDenied("You can only assign your own groups")
        
        serializer.save(advisor=self.request.user)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an assignment (stop future generations)"""
        assignment = self.get_object()
        if request.user != assignment.advisor:
            return Response(
                {'error': 'You can only deactivate your own assignments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        assignment.is_active = False
        assignment.save()
        
        return Response({
            'message': f'Assignment of "{assignment.group.name}" to "{assignment.template.title}" has been deactivated'
        })
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate an assignment"""
        assignment = self.get_object()
        if request.user != assignment.advisor:
            return Response(
                {'error': 'You can only reactivate your own assignments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        assignment.is_active = True
        assignment.save()
        
        return Response({
            'message': f'Assignment of "{assignment.group.name}" to "{assignment.template.title}" has been reactivated'
        })


class GeneratedSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing generated sessions (read-only)"""
    
    serializer_class = GeneratedSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter generated sessions based on user role"""
        user = self.request.user
        
        if user.role == 'teacher':
            # Teachers see sessions generated from their templates
            return GeneratedSession.objects.filter(template__teacher=user)
        elif user.role == 'advisor':
            # Advisors see sessions from templates they've assigned groups to
            return GeneratedSession.objects.filter(
                template__group_assignments__advisor=user,
                template__group_assignments__is_active=True
            ).distinct()
        elif user.role == 'student':
            # Students see sessions they're assigned to
            return GeneratedSession.objects.filter(
                session__assignments__student=user
            )
        else:
            return GeneratedSession.objects.none()


class TemplateGenerationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing generation logs (read-only, admin only)"""
    
    serializer_class = TemplateGenerationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow teachers to see logs for their templates"""
        user = self.request.user
        
        if user.role == 'teacher':
            return TemplateGenerationLog.objects.filter(template__teacher=user)
        else:
            return TemplateGenerationLog.objects.none()


# Utility views for dropdowns and selections
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_students(request):
    """Get list of students available for group assignment"""
    print(f"DEBUG: get_available_students called by user {request.user.email} with role {request.user.role}")
    
    if request.user.role != 'advisor':
        print(f"DEBUG: Access denied - user role is {request.user.role}, not advisor")
        return Response(
            {'error': 'Only advisors can view students'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    from ..models.user_model import User
    students = User.objects.filter(role='student').order_by('first_name', 'last_name')
    print(f"DEBUG: Found {students.count()} students")
    
    # Add search functionality
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
        print(f"DEBUG: After search filter: {students.count()} students")
    
    serializer = StudentSimpleSerializer(students, many=True)
    print(f"DEBUG: Serialized data: {serializer.data}")
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_recurring_sessions(request):
    """Get recurring sessions assigned to the current student"""
    print(f"DEBUG: get_my_recurring_sessions called by {request.user.email}")
    
    if request.user.role != 'student':
        return Response(
            {'error': 'Only students can view their assigned sessions'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get templates assigned to this student through groups
    templates = SessionTemplate.objects.filter(
        group_assignments__group__students=request.user,
        group_assignments__is_active=True
    ).distinct()
    
    print(f"DEBUG: Found {templates.count()} templates for student {request.user.email}")
    
    # Serialize with additional info
    data = []
    for template in templates:
        data.append({
            'id': template.id,
            'title': template.title,
            'description': template.description,
            'subject': template.subject,
            'level': template.level,
            'day_of_week_display': template.get_day_of_week_display(),
            'start_time': template.start_time,
            'duration_minutes': template.duration_minutes,
            'recurrence_type': template.recurrence_type,
            'status': template.status,
            'teacher_name': f"{template.teacher.first_name} {template.teacher.last_name}",
            'next_generation_date': template.next_generation_date,
            'created_at': template.created_at
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_template_statistics(request):
    """Get statistics about templates and generated sessions"""
    user = request.user
    
    if user.role == 'teacher':
        templates = SessionTemplate.objects.filter(teacher=user)
        generated_sessions = GeneratedSession.objects.filter(template__teacher=user)
    elif user.role == 'advisor':
        templates = SessionTemplate.objects.filter(
            group_assignments__advisor=user,
            group_assignments__is_active=True
        ).distinct()
        generated_sessions = GeneratedSession.objects.filter(
            template__group_assignments__advisor=user,
            template__group_assignments__is_active=True
        ).distinct()
    else:
        return Response(
            {'error': 'Access denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = {
        'total_templates': templates.count(),
        'active_templates': templates.filter(status='ACTIVE').count(),
        'paused_templates': templates.filter(status='PAUSED').count(),
        'ended_templates': templates.filter(status='ENDED').count(),
        'total_generated_sessions': generated_sessions.count(),
        'upcoming_sessions': generated_sessions.filter(
            session__scheduled_datetime__gt=timezone.now()
        ).count(),
        'completed_sessions': generated_sessions.filter(
            session__status='COMPLETED'
        ).count(),
    }
    
    return Response(stats)