"""
Admin configuration for activities app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count

from .models import ActivityType, Activity, Task, InteractionLog, FollowUpRule


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    """Admin for ActivityType model."""
    
    list_display = [
        'name', 'color_display', 'is_active', 'requires_duration', 
        'requires_outcome', 'activities_count', 'created_at'
    ]
    list_filter = ['is_active', 'requires_duration', 'requires_outcome']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Display Settings', {
            'fields': ('color', 'is_active')
        }),
        ('Requirements', {
            'fields': ('requires_duration', 'requires_outcome')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            activities_count=Count('activities')
        )
    
    def activities_count(self, obj):
        """Display number of activities for this type."""
        return obj.activities_count
    activities_count.short_description = 'Activities'
    
    def color_display(self, obj):
        """Display color as a colored box."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin for Activity model."""
    
    list_display = [
        'title', 'activity_type', 'status_display', 'priority_display',
        'assigned_to', 'scheduled_at', 'contact', 'is_overdue_display'
    ]
    list_filter = [
        'status', 'priority', 'activity_type', 'assigned_to',
        'requires_follow_up', 'reminder_sent'
    ]
    search_fields = ['title', 'description', 'contact__first_name', 'contact__last_name']
    ordering = ['-scheduled_at']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'reminder_sent']
    date_hierarchy = 'scheduled_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'activity_type')
        }),
        ('Scheduling', {
            'fields': ('scheduled_at', 'duration_minutes', 'status', 'priority')
        }),
        ('Relationships', {
            'fields': ('contact', 'company', 'opportunity', 'assigned_to')
        }),
        ('Completion', {
            'fields': ('completed_at', 'outcome', 'outcome_notes'),
            'classes': ('collapse',)
        }),
        ('Follow-up', {
            'fields': ('requires_follow_up', 'follow_up_date', 'parent_activity'),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': ('reminder_minutes_before', 'reminder_sent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'activity_type', 'contact', 'company', 'opportunity',
            'assigned_to', 'created_by'
        )
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'scheduled': '#3B82F6',
            'in_progress': '#F59E0B', 
            'completed': '#10B981',
            'cancelled': '#6B7280',
            'overdue': '#EF4444'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def priority_display(self, obj):
        """Display priority with color coding."""
        colors = {
            'low': '#6B7280',
            'medium': '#F59E0B',
            'high': '#EF4444',
            'urgent': '#DC2626'
        }
        color = colors.get(obj.priority, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    
    def is_overdue_display(self, obj):
        """Display overdue status."""
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠️ Overdue</span>')
        return format_html('<span style="color: green;">✓ On time</span>')
    is_overdue_display.short_description = 'Status'
    
    actions = ['mark_completed', 'mark_cancelled', 'send_reminders']
    
    def mark_completed(self, request, queryset):
        """Bulk action to mark activities as completed."""
        updated = 0
        for activity in queryset.filter(status__in=['scheduled', 'in_progress']):
            activity.mark_completed(user=request.user)
            updated += 1
        
        self.message_user(
            request,
            f'{updated} activity(ies) marked as completed.'
        )
    mark_completed.short_description = "Mark selected activities as completed"
    
    def mark_cancelled(self, request, queryset):
        """Bulk action to mark activities as cancelled."""
        updated = queryset.filter(
            status__in=['scheduled', 'in_progress']
        ).update(status='cancelled')
        
        self.message_user(
            request,
            f'{updated} activity(ies) marked as cancelled.'
        )
    mark_cancelled.short_description = "Mark selected activities as cancelled"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model."""
    
    list_display = [
        'title', 'status_display', 'priority_display', 'assigned_to',
        'due_date', 'is_overdue_display', 'created_at'
    ]
    list_filter = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description', 'contact__first_name', 'contact__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Assignment & Priority', {
            'fields': ('assigned_to', 'priority', 'status', 'due_date')
        }),
        ('Relationships', {
            'fields': ('contact', 'company', 'opportunity'),
            'classes': ('collapse',)
        }),
        ('Completion', {
            'fields': ('completed_at', 'completion_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'contact', 'company', 'opportunity',
            'assigned_to', 'created_by'
        )
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'todo': '#F59E0B',
            'in_progress': '#3B82F6',
            'completed': '#10B981',
            'cancelled': '#6B7280'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def priority_display(self, obj):
        """Display priority with color coding."""
        colors = {
            'low': '#6B7280',
            'medium': '#F59E0B',
            'high': '#EF4444',
            'urgent': '#DC2626'
        }
        color = colors.get(obj.priority, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    
    def is_overdue_display(self, obj):
        """Display overdue status."""
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠️ Overdue</span>')
        return format_html('<span style="color: green;">✓ On time</span>')
    is_overdue_display.short_description = 'Status'
    
    actions = ['mark_completed', 'mark_cancelled']
    
    def mark_completed(self, request, queryset):
        """Bulk action to mark tasks as completed."""
        updated = 0
        for task in queryset.filter(status__in=['todo', 'in_progress']):
            task.mark_completed()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} task(s) marked as completed.'
        )
    mark_completed.short_description = "Mark selected tasks as completed"
    
    def mark_cancelled(self, request, queryset):
        """Bulk action to mark tasks as cancelled."""
        updated = queryset.filter(
            status__in=['todo', 'in_progress']
        ).update(status='cancelled')
        
        self.message_user(
            request,
            f'{updated} task(s) marked as cancelled.'
        )
    mark_cancelled.short_description = "Mark selected tasks as cancelled"


@admin.register(InteractionLog)
class InteractionLogAdmin(admin.ModelAdmin):
    """Admin for InteractionLog model."""
    
    list_display = [
        'title', 'interaction_type_display', 'interaction_date',
        'contact', 'company', 'logged_by', 'duration_minutes'
    ]
    list_filter = ['interaction_type', 'logged_by', 'interaction_date']
    search_fields = ['title', 'notes', 'contact__first_name', 'contact__last_name']
    ordering = ['-interaction_date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'interaction_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'interaction_type', 'notes')
        }),
        ('Timing', {
            'fields': ('interaction_date', 'duration_minutes')
        }),
        ('Relationships', {
            'fields': ('contact', 'company', 'opportunity', 'source_activity')
        }),
        ('Tracking', {
            'fields': ('logged_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'contact', 'company', 'opportunity', 'logged_by', 'source_activity'
        )
    
    def interaction_type_display(self, obj):
        """Display interaction type with icon."""
        icons = {
            'call_inbound': '📞',
            'call_outbound': '📲',
            'email_sent': '📧',
            'email_received': '📨',
            'meeting': '🤝',
            'note': '📝',
            'sms': '💬',
            'other': '📋'
        }
        icon = icons.get(obj.interaction_type, '📋')
        return format_html(
            '{} {}',
            icon,
            obj.get_interaction_type_display()
        )
    interaction_type_display.short_description = 'Type'


@admin.register(FollowUpRule)
class FollowUpRuleAdmin(admin.ModelAdmin):
    """Admin for FollowUpRule model."""
    
    list_display = [
        'name', 'trigger_activity_type', 'trigger_outcome_display',
        'follow_up_activity_type', 'follow_up_delay_days', 'is_active'
    ]
    list_filter = ['is_active', 'trigger_activity_type', 'follow_up_activity_type']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Trigger Conditions', {
            'fields': ('trigger_activity_type', 'trigger_outcome')
        }),
        ('Follow-up Settings', {
            'fields': (
                'follow_up_activity_type', 'follow_up_delay_days',
                'follow_up_title_template', 'follow_up_description_template'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def trigger_outcome_display(self, obj):
        """Display trigger outcome."""
        return obj.get_trigger_outcome_display()
    trigger_outcome_display.short_description = 'Trigger Outcome'


# Custom admin views for better management

class ActivityInline(admin.TabularInline):
    """Inline for displaying activities in related models."""
    model = Activity
    fields = ['title', 'activity_type', 'scheduled_at', 'status', 'assigned_to']
    readonly_fields = ['title', 'activity_type', 'scheduled_at', 'status']
    extra = 0
    can_delete = False
    max_num = 5
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'activity_type', 'assigned_to'
        ).order_by('-scheduled_at')


class TaskInline(admin.TabularInline):
    """Inline for displaying tasks in related models."""
    model = Task
    fields = ['title', 'status', 'priority', 'due_date', 'assigned_to']
    readonly_fields = ['title', 'status', 'priority', 'due_date']
    extra = 0
    can_delete = False
    max_num = 5
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assigned_to'
        ).order_by('-created_at')


class InteractionLogInline(admin.TabularInline):
    """Inline for displaying interaction logs in related models."""
    model = InteractionLog
    fields = ['title', 'interaction_type', 'interaction_date', 'logged_by']
    readonly_fields = ['title', 'interaction_type', 'interaction_date', 'logged_by']
    extra = 0
    can_delete = False
    max_num = 5
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'logged_by'
        ).order_by('-interaction_date')