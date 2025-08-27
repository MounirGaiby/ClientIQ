"""
Views for activities app.
"""

from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal

from apps.users.models import CustomUser

from .models import ActivityType, Activity, Task, InteractionLog, FollowUpRule
from .serializers import (
    ActivityTypeSerializer,
    ActivitySerializer, ActivityListSerializer, ActivityCreateUpdateSerializer,
    ActivityCompletionSerializer,
    TaskSerializer, TaskListSerializer, TaskCreateUpdateSerializer,
    TaskCompletionSerializer,
    InteractionLogSerializer, InteractionLogListSerializer,
    InteractionLogCreateUpdateSerializer,
    FollowUpRuleSerializer, FollowUpRuleCreateUpdateSerializer,
    ActivityStatsSerializer, TaskStatsSerializer, InteractionStatsSerializer,
    CombinedStatsSerializer
)


class ActivityTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing activity types.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Get all activity types, optionally filtered by active status."""
        queryset = ActivityType.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def create_default_types(self, request):
        """Create default activity types for a new tenant."""
        default_types = [
            {
                'name': 'Call',
                'description': 'Phone call with contact',
                'icon': 'phone',
                'color': '#10B981',
                'requires_duration': True,
                'requires_outcome': True
            },
            {
                'name': 'Email',
                'description': 'Email communication',
                'icon': 'mail',
                'color': '#3B82F6',
                'requires_duration': False,
                'requires_outcome': True
            },
            {
                'name': 'Meeting',
                'description': 'In-person or virtual meeting',
                'icon': 'calendar',
                'color': '#8B5CF6',
                'requires_duration': True,
                'requires_outcome': True
            },
            {
                'name': 'Task',
                'description': 'General task or follow-up',
                'icon': 'check-square',
                'color': '#F59E0B',
                'requires_duration': False,
                'requires_outcome': False
            },
            {
                'name': 'Note',
                'description': 'Add a note or comment',
                'icon': 'edit',
                'color': '#6B7280',
                'requires_duration': False,
                'requires_outcome': False
            }
        ]
        
        created_types = []
        for type_data in default_types:
            activity_type, created = ActivityType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                created_types.append(activity_type)
        
        serializer = ActivityTypeSerializer(created_types, many=True)
        return Response({
            'message': f'Created {len(created_types)} default activity types',
            'types': serializer.data
        })


class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing activities.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'activity_type', 'assigned_to', 'contact', 'company', 'opportunity']
    search_fields = ['title', 'description']
    ordering_fields = ['scheduled_at', 'created_at', 'priority']
    ordering = ['-scheduled_at']
    
    def get_queryset(self):
        """Get activities with optimized queries."""
        queryset = Activity.objects.select_related(
            'activity_type', 'contact', 'company', 'opportunity',
            'assigned_to', 'created_by'
        ).prefetch_related('follow_up_activities')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(scheduled_at__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(scheduled_at__lte=end_date)
            except ValueError:
                pass
        
        # Filter by overdue
        is_overdue = self.request.query_params.get('is_overdue')
        if is_overdue == 'true':
            queryset = queryset.filter(
                scheduled_at__lt=timezone.now(),
                status__in=['scheduled', 'in_progress']
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ActivityListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ActivityCreateUpdateSerializer
        return ActivitySerializer
    
    def perform_create(self, serializer):
        """Set created_by when creating an activity."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark activity as completed with outcome."""
        activity = self.get_object()
        
        if activity.status == 'completed':
            return Response(
                {'detail': 'Activity is already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ActivityCompletionSerializer(data=request.data)
        if serializer.is_valid():
            activity.mark_completed(
                outcome=serializer.validated_data.get('outcome'),
                outcome_notes=serializer.validated_data.get('outcome_notes', ''),
                user=request.user
            )
            
            # Create interaction log
            if activity.contact or activity.company:
                InteractionLog.objects.create(
                    title=f"Completed: {activity.title}",
                    interaction_type='other',  # Could be mapped based on activity type
                    notes=f"Activity completed with outcome: {activity.get_outcome_display()}. Notes: {activity.outcome_notes}",
                    interaction_date=activity.completed_at,
                    contact=activity.contact,
                    company=activity.company,
                    opportunity=activity.opportunity,
                    logged_by=request.user,
                    source_activity=activity
                )
            
            # Check for automatic follow-up rules
            self._apply_follow_up_rules(activity)
            
            return Response({
                'detail': 'Activity completed successfully.',
                'activity': ActivitySerializer(activity).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _apply_follow_up_rules(self, activity):
        """Apply automatic follow-up rules for completed activity."""
        if not activity.outcome:
            return
        
        rules = FollowUpRule.objects.filter(
            is_active=True,
            trigger_activity_type=activity.activity_type,
            trigger_outcome=activity.outcome
        )
        
        for rule in rules:
            rule.create_follow_up(activity)
    
    @action(detail=False, methods=['get'])
    def my_activities(self, request):
        """Get activities assigned to current user."""
        activities = self.get_queryset().filter(assigned_to=request.user)
        
        # Additional filters
        status_filter = request.query_params.get('status')
        if status_filter:
            activities = activities.filter(status=status_filter)
        
        priority_filter = request.query_params.get('priority')
        if priority_filter:
            activities = activities.filter(priority=priority_filter)
        
        serializer = ActivityListSerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get activities scheduled for today."""
        today = timezone.now().date()
        activities = self.get_queryset().filter(
            scheduled_at__date=today
        ).order_by('scheduled_at')
        
        serializer = ActivityListSerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue activities."""
        overdue_activities = self.get_queryset().filter(
            scheduled_at__lt=timezone.now(),
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_at')
        
        serializer = ActivityListSerializer(overdue_activities, many=True)
        return Response({
            'count': overdue_activities.count(),
            'activities': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming activities (next 7 days)."""
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        upcoming_activities = self.get_queryset().filter(
            scheduled_at__range=[start_date, end_date],
            status='scheduled'
        ).order_by('scheduled_at')
        
        serializer = ActivityListSerializer(upcoming_activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get activity statistics for current user."""
        user_activities = self.get_queryset().filter(assigned_to=request.user)
        
        # Calculate date ranges
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Basic counts
        total_activities = user_activities.count()
        completed_activities = user_activities.filter(status='completed').count()
        overdue_activities = user_activities.filter(
            scheduled_at__lt=timezone.now(),
            status__in=['scheduled', 'in_progress']
        ).count()
        scheduled_today = user_activities.filter(
            scheduled_at__date=today,
            status='scheduled'
        ).count()
        scheduled_this_week = user_activities.filter(
            scheduled_at__date__range=[week_start, week_end],
            status='scheduled'
        ).count()
        
        # Completion rate
        completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        # By type breakdown
        activities_by_type = list(
            user_activities.values('activity_type__name', 'activity_type__color')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # By status breakdown
        activities_by_status = list(
            user_activities.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Recent completions
        recent_completions = user_activities.filter(
            status='completed'
        ).order_by('-completed_at')[:5]
        
        # Upcoming activities
        upcoming_activities = user_activities.filter(
            scheduled_at__gte=timezone.now(),
            status='scheduled'
        ).order_by('scheduled_at')[:5]
        
        stats_data = {
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'overdue_activities': overdue_activities,
            'scheduled_today': scheduled_today,
            'scheduled_this_week': scheduled_this_week,
            'completion_rate': Decimal(str(completion_rate)),
            'activities_by_type': activities_by_type,
            'activities_by_status': activities_by_status,
            'recent_completions': ActivityListSerializer(recent_completions, many=True).data,
            'upcoming_activities': ActivityListSerializer(upcoming_activities, many=True).data
        }
        
        serializer = ActivityStatsSerializer(stats_data)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'contact', 'company', 'opportunity']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get tasks with optimized queries."""
        queryset = Task.objects.select_related(
            'contact', 'company', 'opportunity',
            'assigned_to', 'created_by'
        )
        
        # Filter by due date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
                queryset = queryset.filter(due_date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
                queryset = queryset.filter(due_date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by overdue
        is_overdue = self.request.query_params.get('is_overdue')
        if is_overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['todo', 'in_progress']
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskSerializer
    
    def get_tenant_user(self, request):
        try:
            return CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return None
    
    def perform_create(self, serializer):
        """Set created_by when creating a task."""
        tenant_user = self.get_tenant_user(self.request)
        serializer.save(created_by=tenant_user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed."""
        task = self.get_object()
        
        if task.status == 'completed':
            return Response(
                {'detail': 'Task is already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TaskCompletionSerializer(data=request.data)
        if serializer.is_valid():
            task.mark_completed(
                notes=serializer.validated_data.get('completion_notes', '')
            )
            
            return Response({
                'detail': 'Task completed successfully.',
                'task': TaskSerializer(task).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user."""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        
        # Additional filters
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        priority_filter = request.query_params.get('priority')
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_today(self, request):
        """Get tasks due today."""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(
            due_date=today,
            status__in=['todo', 'in_progress']
        ).order_by('priority', 'created_at')
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(tasks.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks."""
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status__in=['todo', 'in_progress']
        ).order_by('due_date')
        
        serializer = TaskListSerializer(overdue_tasks, many=True)
        return Response({
            'count': overdue_tasks.count(),
            'tasks': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics for current user."""
        user_tasks = self.get_queryset().filter(assigned_to=request.user)
        
        # Calculate date ranges
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Basic counts
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(status='completed').count()
        overdue_tasks = user_tasks.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress']
        ).count()
        due_today = user_tasks.filter(
            due_date=today,
            status__in=['todo', 'in_progress']
        ).count()
        due_this_week = user_tasks.filter(
            due_date__range=[week_start, week_end],
            status__in=['todo', 'in_progress']
        ).count()
        
        # Completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # By priority breakdown
        tasks_by_priority = list(
            user_tasks.values('priority')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # By status breakdown
        tasks_by_status = list(
            user_tasks.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Recent completions
        recent_completions = user_tasks.filter(
            status='completed'
        ).order_by('-completed_at')[:5]
        
        # Upcoming tasks
        upcoming_tasks = user_tasks.filter(
            due_date__gte=today,
            status__in=['todo', 'in_progress']
        ).order_by('due_date')[:5]
        
        stats_data = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'due_today': due_today,
            'due_this_week': due_this_week,
            'completion_rate': Decimal(str(completion_rate)),
            'tasks_by_priority': tasks_by_priority,
            'tasks_by_status': tasks_by_status,
            'recent_completions': TaskListSerializer(recent_completions, many=True).data,
            'upcoming_tasks': TaskListSerializer(upcoming_tasks, many=True).data
        }
        
        serializer = TaskStatsSerializer(stats_data)
        return Response(serializer.data)


class InteractionLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing interaction logs.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['interaction_type', 'contact', 'company', 'opportunity', 'logged_by']
    search_fields = ['title', 'notes']
    ordering_fields = ['interaction_date', 'created_at']
    ordering = ['-interaction_date']
    
    def get_queryset(self):
        """Get interaction logs with optimized queries."""
        queryset = InteractionLog.objects.select_related(
            'contact', 'company', 'opportunity',
            'logged_by', 'source_activity'
        )
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(interaction_date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(interaction_date__lte=end_date)
            except ValueError:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return InteractionLogListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InteractionLogCreateUpdateSerializer
        return InteractionLogSerializer
    
    def perform_create(self, serializer):
        """Set logged_by when creating an interaction log."""
        serializer.save(logged_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get interaction statistics for current user."""
        user_interactions = self.get_queryset().filter(logged_by=request.user)
        
        # Calculate date ranges
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        month_start = today.replace(day=1)
        
        # Basic counts
        total_interactions = user_interactions.count()
        interactions_this_week = user_interactions.filter(
            interaction_date__date__range=[week_start, week_end]
        ).count()
        interactions_this_month = user_interactions.filter(
            interaction_date__date__gte=month_start
        ).count()
        
        # Average duration
        avg_duration = user_interactions.filter(
            duration_minutes__isnull=False
        ).aggregate(avg=Avg('duration_minutes'))['avg'] or 0
        
        # By type breakdown
        interactions_by_type = list(
            user_interactions.values('interaction_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Daily interactions for last 30 days
        daily_interactions = []
        for i in range(30):
            check_date = today - timedelta(days=i)
            daily_count = user_interactions.filter(
                interaction_date__date=check_date
            ).count()
            daily_interactions.append({
                'date': check_date.isoformat(),
                'count': daily_count
            })
        
        # Recent interactions
        recent_interactions = user_interactions.order_by('-interaction_date')[:5]
        
        stats_data = {
            'total_interactions': total_interactions,
            'interactions_this_week': interactions_this_week,
            'interactions_this_month': interactions_this_month,
            'average_duration': Decimal(str(avg_duration)),
            'interactions_by_type': interactions_by_type,
            'daily_interactions': daily_interactions,
            'recent_interactions': InteractionLogListSerializer(recent_interactions, many=True).data
        }
        
        serializer = InteractionStatsSerializer(stats_data)
        return Response(serializer.data)


class FollowUpRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing follow-up rules.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Get all follow-up rules."""
        queryset = FollowUpRule.objects.select_related(
            'trigger_activity_type', 'follow_up_activity_type'
        )
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return FollowUpRuleCreateUpdateSerializer
        return FollowUpRuleSerializer


# Dashboard and Combined Views

class DashboardStatsView(generics.RetrieveAPIView):
    """
    Combined statistics view for activity dashboard.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get combined statistics for dashboard."""
        user = request.user
        
        # Get individual stats
        activity_stats = self._get_activity_stats(user)
        task_stats = self._get_task_stats(user)
        interaction_stats = self._get_interaction_stats(user)
        
        # Calculate productivity score (0-100)
        productivity_score = self._calculate_productivity_score(
            activity_stats, task_stats, interaction_stats
        )
        
        # Weekly trend
        weekly_trend = self._calculate_weekly_trend(user)
        
        # Today's agenda
        todays_agenda = self._get_todays_agenda(user)
        
        # Overdue items
        overdue_items = self._get_overdue_items(user)
        
        combined_stats = {
            'activity_stats': activity_stats,
            'task_stats': task_stats,
            'interaction_stats': interaction_stats,
            'productivity_score': productivity_score,
            'weekly_activity_trend': weekly_trend,
            'todays_agenda': todays_agenda,
            'overdue_items': overdue_items
        }
        
        serializer = CombinedStatsSerializer(combined_stats)
        return Response(serializer.data)
    
    def _get_activity_stats(self, user):
        """Get activity statistics for user."""
        user_activities = Activity.objects.filter(assigned_to=user)
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        total_activities = user_activities.count()
        completed_activities = user_activities.filter(status='completed').count()
        overdue_activities = user_activities.filter(
            scheduled_at__lt=timezone.now(),
            status__in=['scheduled', 'in_progress']
        ).count()
        scheduled_today = user_activities.filter(
            scheduled_at__date=today,
            status='scheduled'
        ).count()
        scheduled_this_week = user_activities.filter(
            scheduled_at__date__range=[week_start, week_end],
            status='scheduled'
        ).count()
        
        completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        activities_by_type = list(
            user_activities.values('activity_type__name', 'activity_type__color')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        activities_by_status = list(
            user_activities.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        recent_completions = ActivityListSerializer(
            user_activities.filter(status='completed').order_by('-completed_at')[:5],
            many=True
        ).data
        
        upcoming_activities = ActivityListSerializer(
            user_activities.filter(
                scheduled_at__gte=timezone.now(),
                status='scheduled'
            ).order_by('scheduled_at')[:5],
            many=True
        ).data
        
        return {
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'overdue_activities': overdue_activities,
            'scheduled_today': scheduled_today,
            'scheduled_this_week': scheduled_this_week,
            'completion_rate': Decimal(str(completion_rate)),
            'activities_by_type': activities_by_type,
            'activities_by_status': activities_by_status,
            'recent_completions': recent_completions,
            'upcoming_activities': upcoming_activities
        }
    
    def _get_task_stats(self, user):
        """Get task statistics for user."""
        user_tasks = Task.objects.filter(assigned_to=user)
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(status='completed').count()
        overdue_tasks = user_tasks.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress']
        ).count()
        due_today = user_tasks.filter(
            due_date=today,
            status__in=['todo', 'in_progress']
        ).count()
        due_this_week = user_tasks.filter(
            due_date__range=[week_start, week_end],
            status__in=['todo', 'in_progress']
        ).count()
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        tasks_by_priority = list(
            user_tasks.values('priority')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        tasks_by_status = list(
            user_tasks.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        recent_completions = TaskListSerializer(
            user_tasks.filter(status='completed').order_by('-completed_at')[:5],
            many=True
        ).data
        
        upcoming_tasks = TaskListSerializer(
            user_tasks.filter(
                due_date__gte=today,
                status__in=['todo', 'in_progress']
            ).order_by('due_date')[:5],
            many=True
        ).data
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'due_today': due_today,
            'due_this_week': due_this_week,
            'completion_rate': Decimal(str(completion_rate)),
            'tasks_by_priority': tasks_by_priority,
            'tasks_by_status': tasks_by_status,
            'recent_completions': recent_completions,
            'upcoming_tasks': upcoming_tasks
        }
    
    def _get_interaction_stats(self, user):
        """Get interaction statistics for user."""
        user_interactions = InteractionLog.objects.filter(logged_by=user)
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        month_start = today.replace(day=1)
        
        total_interactions = user_interactions.count()
        interactions_this_week = user_interactions.filter(
            interaction_date__date__range=[week_start, week_end]
        ).count()
        interactions_this_month = user_interactions.filter(
            interaction_date__date__gte=month_start
        ).count()
        
        avg_duration = user_interactions.filter(
            duration_minutes__isnull=False
        ).aggregate(avg=Avg('duration_minutes'))['avg'] or 0
        
        interactions_by_type = list(
            user_interactions.values('interaction_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Daily interactions for last 30 days
        daily_interactions = []
        for i in range(30):
            check_date = today - timedelta(days=i)
            daily_count = user_interactions.filter(
                interaction_date__date=check_date
            ).count()
            daily_interactions.append({
                'date': check_date.isoformat(),
                'count': daily_count
            })
        
        recent_interactions = InteractionLogListSerializer(
            user_interactions.order_by('-interaction_date')[:5],
            many=True
        ).data
        
        return {
            'total_interactions': total_interactions,
            'interactions_this_week': interactions_this_week,
            'interactions_this_month': interactions_this_month,
            'average_duration': Decimal(str(avg_duration)),
            'interactions_by_type': interactions_by_type,
            'daily_interactions': daily_interactions,
            'recent_interactions': recent_interactions
        }
    
    def _calculate_productivity_score(self, activity_stats, task_stats, interaction_stats):
        """Calculate overall productivity score."""
        # Simple scoring algorithm (can be improved)
        activity_score = min(activity_stats['completion_rate'], 100)
        task_score = min(task_stats['completion_rate'], 100)
        interaction_score = min(interaction_stats['interactions_this_week'] * 10, 100)
        
        # Penalize overdue items
        overdue_penalty = (activity_stats['overdue_activities'] + task_stats['overdue_tasks']) * 5
        
        productivity_score = max(0, (activity_score + task_score + interaction_score) / 3 - overdue_penalty)
        return Decimal(str(min(productivity_score, 100)))
    
    def _calculate_weekly_trend(self, user):
        """Calculate weekly activity trend (percentage change)."""
        today = timezone.now().date()
        
        # Current week
        current_week_start = today - timedelta(days=today.weekday())
        current_week_end = current_week_start + timedelta(days=6)
        
        # Previous week
        prev_week_start = current_week_start - timedelta(days=7)
        prev_week_end = prev_week_start + timedelta(days=6)
        
        current_week_count = Activity.objects.filter(
            assigned_to=user,
            created_at__date__range=[current_week_start, current_week_end]
        ).count() + Task.objects.filter(
            assigned_to=user,
            created_at__date__range=[current_week_start, current_week_end]
        ).count()
        
        prev_week_count = Activity.objects.filter(
            assigned_to=user,
            created_at__date__range=[prev_week_start, prev_week_end]
        ).count() + Task.objects.filter(
            assigned_to=user,
            created_at__date__range=[prev_week_start, prev_week_end]
        ).count()
        
        if prev_week_count == 0:
            return Decimal('100' if current_week_count > 0 else '0')
        
        trend = ((current_week_count - prev_week_count) / prev_week_count) * 100
        return Decimal(str(round(trend, 2)))
    
    def _get_todays_agenda(self, user):
        """Get today's agenda (activities and tasks)."""
        today = timezone.now().date()
        
        # Today's activities
        activities = Activity.objects.filter(
            assigned_to=user,
            scheduled_at__date=today,
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_at')
        
        # Today's tasks
        tasks = Task.objects.filter(
            assigned_to=user,
            due_date=today,
            status__in=['todo', 'in_progress']
        ).order_by('priority', 'created_at')
        
        agenda = []
        
        # Add activities
        for activity in activities:
            agenda.append({
                'type': 'activity',
                'id': activity.id,
                'title': activity.title,
                'time': activity.scheduled_at.isoformat(),
                'priority': activity.priority,
                'status': activity.status,
                'duration': activity.duration_minutes,
                'activity_type': activity.activity_type.name,
                'color': activity.activity_type.color
            })
        
        # Add tasks
        for task in tasks:
            agenda.append({
                'type': 'task',
                'id': task.id,
                'title': task.title,
                'time': task.due_date.isoformat() if task.due_date else None,
                'priority': task.priority,
                'status': task.status,
                'duration': None,
                'activity_type': 'Task',
                'color': '#F59E0B'
            })
        
        # Sort by time/priority
        agenda.sort(key=lambda x: (x['time'] or '9999-12-31', x['priority']))
        
        return agenda
    
    def _get_overdue_items(self, user):
        """Get overdue activities and tasks."""
        now = timezone.now()
        today = now.date()
        
        # Overdue activities
        overdue_activities = Activity.objects.filter(
            assigned_to=user,
            scheduled_at__lt=now,
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_at')
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            assigned_to=user,
            due_date__lt=today,
            status__in=['todo', 'in_progress']
        ).order_by('due_date')
        
        overdue_items = []
        
        # Add overdue activities
        for activity in overdue_activities:
            overdue_items.append({
                'type': 'activity',
                'id': activity.id,
                'title': activity.title,
                'time': activity.scheduled_at.isoformat(),
                'priority': activity.priority,
                'status': activity.status,
                'activity_type': activity.activity_type.name,
                'color': activity.activity_type.color,
                'days_overdue': (now.date() - activity.scheduled_at.date()).days
            })
        
        # Add overdue tasks
        for task in overdue_tasks:
            overdue_items.append({
                'type': 'task',
                'id': task.id,
                'title': task.title,
                'time': task.due_date.isoformat() if task.due_date else None,
                'priority': task.priority,
                'status': task.status,
                'activity_type': 'Task',
                'color': '#EF4444',
                'days_overdue': (today - task.due_date).days if task.due_date else 0
            })
        
        # Sort by days overdue (most overdue first)
        overdue_items.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return overdue_items


# Contact/Company/Opportunity Activity Views

class ContactActivityListView(generics.ListAPIView):
    """Get all activities for a specific contact."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-scheduled_at']
    
    def get_queryset(self):
        contact_id = self.kwargs['contact_id']
        return Activity.objects.filter(
            contact_id=contact_id
        ).select_related(
            'activity_type', 'assigned_to', 'created_by'
        )


class ContactInteractionListView(generics.ListAPIView):
    """Get all interactions for a specific contact."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = InteractionLogListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-interaction_date']
    
    def get_queryset(self):
        contact_id = self.kwargs['contact_id']
        return InteractionLog.objects.filter(
            contact_id=contact_id
        ).select_related('logged_by')


class OpportunityActivityListView(generics.ListAPIView):
    """Get all activities for a specific opportunity."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-scheduled_at']
    
    def get_queryset(self):
        opportunity_id = self.kwargs['opportunity_id']
        return Activity.objects.filter(
            opportunity_id=opportunity_id
        ).select_related(
            'activity_type', 'assigned_to', 'created_by'
        )


class OpportunityInteractionListView(generics.ListAPIView):
    """Get all interactions for a specific opportunity."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = InteractionLogListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-interaction_date']
    
    def get_queryset(self):
        opportunity_id = self.kwargs['opportunity_id']
        return InteractionLog.objects.filter(
            opportunity_id=opportunity_id
        ).select_related('logged_by')