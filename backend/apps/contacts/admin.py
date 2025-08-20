"""
Django admin configuration for Contacts app.
"""

from django.contrib import admin
from .models import Company, Contact, ContactTag, ContactTagAssignment


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin interface for Company model"""
    
    list_display = [
        'name', 'industry', 'size', 'city', 'country', 
        'created_at', 'created_by'
    ]
    
    list_filter = [
        'industry', 'size', 'country', 'created_at'
    ]
    
    search_fields = [
        'name', 'website', 'industry', 'city', 'country'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'website', 'industry', 'size')
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city', 
                'state', 'postal_code', 'country'
            )
        }),
        ('Contact', {
            'fields': ('phone',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields"""
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin interface for Contact model"""
    
    list_display = [
        'last_name', 'first_name', 'email', 'company_name', 
        'contact_type', 'score', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'contact_type', 'is_active', 'score', 'created_at', 'company'
    ]
    
    search_fields = [
        'first_name', 'last_name', 'email', 'company__name', 'job_title'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Professional Information', {
            'fields': ('job_title', 'company', 'linkedin_url')
        }),
        ('Classification', {
            'fields': ('contact_type', 'score', 'is_active')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('owner', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Set owner, created_by and updated_by fields"""
        if not change:  # Creating new object
            obj.created_by = request.user
            if not obj.owner:
                obj.owner = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def company_name(self, obj):
        """Display company name in list view"""
        return obj.company.name if obj.company else "-"
    company_name.short_description = "Company"
    
    def get_score_level(self, obj):
        """Display score level in list view"""
        return obj.get_score_level()
    get_score_level.short_description = "Score Level"


class ContactTagAssignmentInline(admin.TabularInline):
    """Inline admin for contact tag assignments"""
    model = ContactTagAssignment
    extra = 1
    readonly_fields = ['assigned_at', 'assigned_by']
    
    def save_model(self, request, obj, form, change):
        """Set assigned_by field"""
        if not change:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContactTag)
class ContactTagAdmin(admin.ModelAdmin):
    """Admin interface for ContactTag model"""
    
    list_display = ['name', 'color', 'contact_count', 'created_at', 'created_by']
    search_fields = ['name']
    readonly_fields = ['created_at', 'created_by']
    
    inlines = [ContactTagAssignmentInline]
    
    def save_model(self, request, obj, form, change):
        """Set created_by field"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def contact_count(self, obj):
        """Display number of contacts with this tag"""
        return obj.contact_assignments.count()
    contact_count.short_description = "Contact Count"


@admin.register(ContactTagAssignment)
class ContactTagAssignmentAdmin(admin.ModelAdmin):
    """Admin interface for ContactTagAssignment model"""
    
    list_display = ['contact', 'tag', 'assigned_at', 'assigned_by']
    list_filter = ['tag', 'assigned_at']
    search_fields = ['contact__first_name', 'contact__last_name', 'tag__name']
    readonly_fields = ['assigned_at', 'assigned_by']
    
    def save_model(self, request, obj, form, change):
        """Set assigned_by field"""
        if not change:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)
