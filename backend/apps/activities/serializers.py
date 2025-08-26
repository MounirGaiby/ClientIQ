"""
Serializers for activities app.
"""

from rest_framework import serializers
from django.utils import timezone
from apps.users.serializers import UserSerializer
from apps.contacts.serializers import ContactListSerializer, CompanySerializer
from apps.opportunities.serializers import OpportunitySerializer

from .models import ActivityType, Activity, Task, InteractionLog, FollowUpRule


class ActivityTypeSerializer(serializers.ModelSerializer):
    """Serializer for ActivityType model."""
    
    class Meta:
        model = ActivityType
        fields = [
            'id', 'name', 'description', 'icon', 'color', 'is_active',
            'requires_duration', 'requires_outcome', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ActivityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating activities."""
    
    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'activity_type', 'scheduled_at',
            'duration_minutes', 'priority', 'contact', 'company', 
            'opportunity', 'assigned_to', 'reminder_minutes_before',
            'requires_follow_up', 'follow_up_date'
        ]
    
    def validate_scheduled_at(self, value):
        """Validate scheduled_at is not in the past."""
        if value < timezone.now():
            raise serializers.ValidationError(
                "Scheduled time cannot be in the past."
            )
        return value
    
    def validate_follow_up_date(self, value):
        """Validate follow_up_date if requires_follow_up is True."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Follow-up date must be in the future."
            )
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        requires_follow_up = data.get('requires_follow_up', False)
        follow_up_date = data.get('follow_up_date')
        
        if requires_follow_up and not follow_up_date:
            raise serializers.ValidationError({
                'follow_up_date': 'Follow-up date is required when follow-up is enabled.'
            })
        
        return data


class ActivitySerializer(serializers.ModelSerializer):
    """Full serializer for Activity model with related objects."""
    
    activity_type = ActivityTypeSerializer(read_only=True)
    contact = ContactListSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    opportunity = OpportunitySerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    # Computed fields
    is_overdue = serializers.ReadOnlyField()
    end_time = serializers.ReadOnlyField()
    reminder_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'description', 'activity_type', 'scheduled_at',
            'duration_minutes', 'status', 'priority', 'contact', 'company',
            'opportunity', 'assigned_to', 'created_by', 'completed_at',
            'outcome', 'outcome_notes', 'reminder_minutes_before', 
            'reminder_sent', 'requires_follow_up', 'follow_up_date',
            'parent_activity', 'is_overdue', 'end_time', 'reminder_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'completed_at', 'reminder_sent',
            'is_overdue', 'end_time', 'reminder_time', 'created_at', 'updated_at'
        ]


class ActivityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for activity lists."""
    
    activity_type_name = serializers.CharField(source='activity_type.name', read_only=True)
    activity_type_color = serializers.CharField(source='activity_type.color', read_only=True)
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    # Computed fields
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'activity_type_name', 'activity_type_color',
            'scheduled_at', 'duration_minutes', 'status', 'priority',
            'contact_name', 'company_name', 'opportunity_name',
            'assigned_to_name', 'is_overdue'
        ]
    
    def get_contact_name(self, obj):
        """Get formatted contact name."""
        if obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}".strip()
        return None


class ActivityCompletionSerializer(serializers.Serializer):
    """Serializer for completing activities."""
    
    outcome = serializers.ChoiceField(
        choices=Activity.OUTCOME_CHOICES,
        required=False
    )
    outcome_notes = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )
    
    def validate(self, data):
        """Validate completion data."""
        outcome = data.get('outcome')
        outcome_notes = data.get('outcome_notes', '')
        
        if outcome == 'other' and not outcome_notes.strip():
            raise serializers.ValidationError({
                'outcome_notes': 'Notes are required when outcome is "Other".'
            })
        
        return data


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating tasks."""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'due_date',
            'assigned_to', 'contact', 'company', 'opportunity'
        ]
    
    def validate_due_date(self, value):
        """Validate due_date is not in the past."""
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Due date cannot be in the past."
            )
        return value


class TaskSerializer(serializers.ModelSerializer):
    """Full serializer for Task model with related objects."""
    
    contact = ContactListSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    opportunity = OpportunitySerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    # Computed fields
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'due_date',
            'assigned_to', 'created_by', 'contact', 'company', 'opportunity',
            'completed_at', 'completion_notes', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'completed_at', 'is_overdue',
            'created_at', 'updated_at'
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists."""
    
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    # Computed fields
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 'due_date',
            'contact_name', 'company_name', 'opportunity_name',
            'assigned_to_name', 'is_overdue', 'created_at'
        ]
    
    def get_contact_name(self, obj):
        """Get formatted contact name."""
        if obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}".strip()
        return None


class TaskCompletionSerializer(serializers.Serializer):
    """Serializer for completing tasks."""
    
    completion_notes = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )


class InteractionLogCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating interaction logs."""
    
    class Meta:
        model = InteractionLog
        fields = [
            'title', 'interaction_type', 'notes', 'interaction_date',
            'duration_minutes', 'contact', 'company', 'opportunity'
        ]
    
    def validate_interaction_date(self, value):
        """Validate interaction_date is not in future."""
        if value > timezone.now():
            raise serializers.ValidationError(
                "Interaction date cannot be in the future."
            )
        return value


class InteractionLogSerializer(serializers.ModelSerializer):
    """Full serializer for InteractionLog model with related objects."""
    
    contact = ContactListSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    opportunity = OpportunitySerializer(read_only=True)
    logged_by = UserSerializer(read_only=True)
    source_activity = ActivityListSerializer(read_only=True)
    
    class Meta:
        model = InteractionLog
        fields = [
            'id', 'title', 'interaction_type', 'notes', 'interaction_date',
            'duration_minutes', 'contact', 'company', 'opportunity',
            'logged_by', 'source_activity', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'logged_by', 'source_activity', 'created_at', 'updated_at'
        ]


class InteractionLogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for interaction log lists."""
    
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    logged_by_name = serializers.CharField(source='logged_by.get_full_name', read_only=True)
    
    class Meta:
        model = InteractionLog
        fields = [
            'id', 'title', 'interaction_type', 'interaction_type_display',
            'interaction_date', 'duration_minutes', 'contact_name',
            'company_name', 'opportunity_name', 'logged_by_name'
        ]
    
    def get_contact_name(self, obj):
        """Get formatted contact name."""
        if obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}".strip()
        return None


class FollowUpRuleSerializer(serializers.ModelSerializer):
    """Serializer for FollowUpRule model."""
    
    trigger_activity_type = ActivityTypeSerializer(read_only=True)
    follow_up_activity_type = ActivityTypeSerializer(read_only=True)
    trigger_outcome_display = serializers.CharField(source='get_trigger_outcome_display', read_only=True)
    
    class Meta:
        model = FollowUpRule
        fields = [
            'id', 'name', 'description', 'trigger_activity_type',
            'trigger_outcome', 'trigger_outcome_display', 'follow_up_activity_type',
            'follow_up_delay_days', 'follow_up_title_template',
            'follow_up_description_template', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FollowUpRuleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating follow-up rules."""
    
    class Meta:
        model = FollowUpRule
        fields = [
            'name', 'description', 'trigger_activity_type', 'trigger_outcome',
            'follow_up_activity_type', 'follow_up_delay_days',
            'follow_up_title_template', 'follow_up_description_template',
            'is_active'
        ]
    
    def validate_follow_up_delay_days(self, value):
        """Validate follow-up delay is positive."""
        if value < 1:
            raise serializers.ValidationError(
                "Follow-up delay must be at least 1 day."
            )
        return value


# Statistics and Dashboard Serializers

class ActivityStatsSerializer(serializers.Serializer):
    """Serializer for activity statistics."""
    
    total_activities = serializers.IntegerField()
    completed_activities = serializers.IntegerField()
    overdue_activities = serializers.IntegerField()
    scheduled_today = serializers.IntegerField()
    scheduled_this_week = serializers.IntegerField()
    completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # By type breakdown
    activities_by_type = serializers.ListField(
        child=serializers.DictField()
    )
    
    # By status breakdown
    activities_by_status = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Recent activity
    recent_completions = ActivityListSerializer(many=True, read_only=True)
    upcoming_activities = ActivityListSerializer(many=True, read_only=True)


class TaskStatsSerializer(serializers.Serializer):
    """Serializer for task statistics."""
    
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    due_today = serializers.IntegerField()
    due_this_week = serializers.IntegerField()
    completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # By priority breakdown
    tasks_by_priority = serializers.ListField(
        child=serializers.DictField()
    )
    
    # By status breakdown
    tasks_by_status = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Recent tasks
    recent_completions = TaskListSerializer(many=True, read_only=True)
    upcoming_tasks = TaskListSerializer(many=True, read_only=True)


class InteractionStatsSerializer(serializers.Serializer):
    """Serializer for interaction statistics."""
    
    total_interactions = serializers.IntegerField()
    interactions_this_week = serializers.IntegerField()
    interactions_this_month = serializers.IntegerField()
    average_duration = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    # By type breakdown
    interactions_by_type = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Daily interaction counts for the last 30 days
    daily_interactions = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Recent interactions
    recent_interactions = InteractionLogListSerializer(many=True, read_only=True)


class CombinedStatsSerializer(serializers.Serializer):
    """Combined statistics for dashboard."""
    
    activity_stats = ActivityStatsSerializer()
    task_stats = TaskStatsSerializer()
    interaction_stats = InteractionStatsSerializer()
    
    # Overall productivity metrics
    productivity_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    weekly_activity_trend = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Upcoming items
    todays_agenda = serializers.ListField(
        child=serializers.DictField()
    )
    
    overdue_items = serializers.ListField(
        child=serializers.DictField()
    )