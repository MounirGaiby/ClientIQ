"""
Admin configuration for opportunities app.
"""
from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from .models import SalesStage, Opportunity, OpportunityHistory


@admin.register(SalesStage)
class SalesStageAdmin(admin.ModelAdmin):
    """Admin interface for SalesStage model."""
    
    list_display = [
        'name', 'order', 'probability', 'opportunities_count', 
        'total_value', 'color_display', 'is_active', 'is_closed'
    ]
    list_filter = ['is_active', 'is_closed_won', 'is_closed_lost', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    readonly_fields = ['created_at', 'updated_at', 'opportunities_count', 'total_value']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'order', 'probability')
        }),
        ('Status', {
            'fields': ('is_closed_won', 'is_closed_lost', 'is_active')
        }),
        ('Display', {
            'fields': ('color',)
        }),
        ('Statistics', {
            'fields': ('opportunities_count', 'total_value'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Add aggregated data to queryset."""
        return super().get_queryset(request).annotate(
            opportunities_count=Count('opportunities'),
            total_value=Sum('opportunities__value')
        )
    
    def opportunities_count(self, obj):
        """Display count of opportunities in this stage."""
        return obj.opportunities_count or 0
    opportunities_count.short_description = 'Opportunities'
    opportunities_count.admin_order_field = 'opportunities_count'
    
    def total_value(self, obj):
        """Display total value of opportunities in this stage."""
        value = obj.total_value or 0
        return f"${value:,.2f}"
    total_value.short_description = 'Total Value'
    total_value.admin_order_field = 'total_value'
    
    def color_display(self, obj):
        """Display color as a colored square."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def is_closed(self, obj):
        """Display if stage is closed (won or lost)."""
        if obj.is_closed_won:
            return format_html('<span style="color: green;">✓ Won</span>')
        elif obj.is_closed_lost:
            return format_html('<span style="color: red;">✗ Lost</span>')
        return format_html('<span style="color: gray;">Open</span>')
    is_closed.short_description = 'Status'


class OpportunityHistoryInline(admin.TabularInline):
    """Inline for opportunity history."""
    model = OpportunityHistory
    extra = 0
    readonly_fields = ['action', 'old_stage', 'new_stage', 'old_value', 'new_value', 'changed_by', 'created_at']
    fields = ['created_at', 'action', 'old_stage', 'new_stage', 'changed_by', 'notes']
    ordering = ['-created_at']
    
    def has_add_permission(self, request, obj=None):
        """Disable adding history entries manually."""
        return False


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    """Admin interface for Opportunity model."""
    
    list_display = [
        'name', 'contact', 'company', 'stage', 'owner', 
        'value_display', 'probability', 'priority', 
        'expected_close_date', 'is_overdue', 'created_at'
    ]
    list_filter = [
        'stage', 'priority', 'owner', 'created_at', 
        'expected_close_date', 'actual_close_date'
    ]
    search_fields = [
        'name', 'description', 'contact__first_name', 
        'contact__last_name', 'company__name', 'lead_source'
    ]
    readonly_fields = [
        'weighted_value', 'is_overdue', 'days_in_stage', 'age_days',
        'created_at', 'updated_at', 'created_by', 'updated_by'
    ]
    raw_id_fields = ['contact', 'company', 'owner']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [OpportunityHistoryInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'contact', 'company')
        }),
        ('Financial', {
            'fields': ('value', 'probability', 'weighted_value')
        }),
        ('Sales Process', {
            'fields': ('stage', 'owner', 'priority', 'lead_source')
        }),
        ('Timeline', {
            'fields': ('expected_close_date', 'actual_close_date')
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('is_overdue', 'days_in_stage', 'age_days'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def value_display(self, obj):
        """Display formatted value."""
        return f"${obj.value:,.2f}"
    value_display.short_description = 'Value'
    value_display.admin_order_field = 'value'
    
    def is_overdue(self, obj):
        """Display if opportunity is overdue."""
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠ Overdue</span>')
        return format_html('<span style="color: green;">✓ On Track</span>')
    is_overdue.short_description = 'Status'
    is_overdue.boolean = True
    
    def save_model(self, request, obj, form, change):
        """Set user tracking fields when saving."""
        if not change:  # Creating new
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['mark_high_priority', 'mark_medium_priority', 'mark_low_priority']
    
    def mark_high_priority(self, request, queryset):
        """Bulk action to mark opportunities as high priority."""
        updated = queryset.update(priority='high')
        self.message_user(
            request,
            f'{updated} opportunities marked as high priority.'
        )
    mark_high_priority.short_description = "Mark selected opportunities as high priority"
    
    def mark_medium_priority(self, request, queryset):
        """Bulk action to mark opportunities as medium priority."""
        updated = queryset.update(priority='medium')
        self.message_user(
            request,
            f'{updated} opportunities marked as medium priority.'
        )
    mark_medium_priority.short_description = "Mark selected opportunities as medium priority"
    
    def mark_low_priority(self, request, queryset):
        """Bulk action to mark opportunities as low priority."""
        updated = queryset.update(priority='low')
        self.message_user(
            request,
            f'{updated} opportunities marked as low priority.'
        )
    mark_low_priority.short_description = "Mark selected opportunities as low priority"


@admin.register(OpportunityHistory)
class OpportunityHistoryAdmin(admin.ModelAdmin):
    """Admin interface for OpportunityHistory model."""
    
    list_display = [
        'opportunity', 'action', 'changed_by', 'old_stage', 
        'new_stage', 'value_change', 'created_at'
    ]
    list_filter = ['action', 'created_at', 'old_stage', 'new_stage']
    search_fields = [
        'opportunity__name', 'notes', 'changed_by__first_name', 
        'changed_by__last_name'
    ]
    readonly_fields = [
        'opportunity', 'action', 'old_stage', 'new_stage',
        'old_value', 'new_value', 'old_probability', 'new_probability',
        'changed_by', 'created_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def value_change(self, obj):
        """Display value change if applicable."""
        if obj.old_value is not None and obj.new_value is not None:
            change = obj.new_value - obj.old_value
            if change > 0:
                return format_html(
                    '<span style="color: green;">+${:,.2f}</span>', 
                    change
                )
            elif change < 0:
                return format_html(
                    '<span style="color: red;">${:,.2f}</span>', 
                    change
                )
            return "No change"
        return "-"
    value_change.short_description = 'Value Change'
    
    def has_add_permission(self, request):
        """Disable manual creation of history entries."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of history entries."""
        return False