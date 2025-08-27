"""
Contact serializers for ClientIQ CRM.

Provides serialization and validation for Contact and Company models.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.users.models import CustomUser
from .models import Company, Contact, ContactTag, ContactTagAssignment, ContactType


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    
    full_address = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'website', 'industry', 'size',
            'address_line1', 'address_line2', 'city', 'state', 
            'postal_code', 'country', 'phone', 'notes',
            'full_address', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created this company"""
        if obj.created_by:
            return obj.created_by.full_name
        return None
    
    def get_updated_by_name(self, obj):
        """Get the name of the user who last updated this company"""
        if obj.updated_by:
            return obj.updated_by.full_name
        return None


class ContactTagSerializer(serializers.ModelSerializer):
    """Serializer for ContactTag model"""
    
    contact_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactTag
        fields = ['id', 'name', 'color', 'contact_count', 'created_at', 'created_by']
        read_only_fields = ['created_at', 'created_by']
    
    def get_contact_count(self, obj):
        """Get the number of contacts with this tag"""
        return obj.contact_assignments.count()


class ContactTagAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for ContactTagAssignment model"""
    
    tag_name = serializers.SerializerMethodField()
    tag_color = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactTagAssignment
        fields = ['id', 'tag', 'tag_name', 'tag_color', 'assigned_at', 'assigned_by']
        read_only_fields = ['assigned_at', 'assigned_by']
    
    def get_tag_name(self, obj):
        """Get the tag name"""
        return obj.tag.name
    
    def get_tag_color(self, obj):
        """Get the tag color"""
        return obj.tag.color


class ContactListSerializer(serializers.ModelSerializer):
    """Simplified serializer for contact list views"""
    
    full_name = serializers.ReadOnlyField()
    company_name = serializers.ReadOnlyField()
    score_level = serializers.SerializerMethodField()
    tags = ContactTagAssignmentSerializer(source='tag_assignments', many=True, read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'job_title', 'company', 'company_name', 'contact_type', 'score', 
            'score_level', 'is_active', 'created_at', 'tags'
        ]
    
    def get_score_level(self, obj):
        """Get the score level classification"""
        return obj.get_score_level()


class ContactDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for contact detail views"""
    
    full_name = serializers.ReadOnlyField()
    company_name = serializers.ReadOnlyField()
    company_details = CompanySerializer(source='company', read_only=True)
    score_level = serializers.SerializerMethodField()
    tags = ContactTagAssignmentSerializer(source='tag_assignments', many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'job_title', 'company', 'company_name', 'company_details',
            'contact_type', 'score', 'score_level', 'linkedin_url', 'notes',
            'is_active', 'tags', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'owner', 'owner_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def get_score_level(self, obj):
        """Get the score level classification"""
        return obj.get_score_level()
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created this contact"""
        if obj.created_by:
            return obj.created_by.full_name
        return None
    
    def get_updated_by_name(self, obj):
        """Get the name of the user who last updated this contact"""
        if obj.updated_by:
            return obj.updated_by.full_name
        return None
    
    def get_owner_name(self, obj):
        """Get the name of the contact owner"""
        if obj.owner:
            return obj.owner.full_name
        return None


class ContactCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating contacts"""
    
    # Allow setting tags during creation/update
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of tag IDs to assign to this contact"
    )
    
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'job_title',
            'company', 'contact_type', 'score', 'linkedin_url', 'notes',
            'is_active', 'owner', 'tag_ids'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness within tenant"""
        contact_id = self.instance.id if self.instance else None
        
        # Check if email already exists for another contact
        existing_contact = Contact.objects.filter(email=value).exclude(id=contact_id).first()
        if existing_contact:
            raise serializers.ValidationError(
                "A contact with this email already exists."
            )
        
        return value
    
    def validate_score(self, value):
        """Validate score is between 0 and 100"""
        if not 0 <= value <= 100:
            raise serializers.ValidationError(
                "Score must be between 0 and 100."
            )
        return value
    
    def get_tenant_user(self, request):
        try:
            return CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return None
    
    def create(self, validated_data):
        """Create contact with tags"""
        tenant_user = self.get_tenant_user(self.context['request'])
        tag_ids = validated_data.pop('tag_ids', [])
        
        # Set owner to current user if not provided
        if 'owner' not in validated_data:
            validated_data['owner'] = tenant_user
        
        # Set created_by
        validated_data['created_by'] = tenant_user
        
        contact = Contact.objects.create(**validated_data)
        
        # Assign tags
        self._assign_tags(contact, tag_ids)
        
        return contact
    
    def update(self, instance, validated_data):
        """Update contact with tags"""
        tenant_user = self.get_tenant_user(self.context['request'])
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Set updated_by
        validated_data['updated_by'] = tenant_user
        
        # Update contact fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tag_ids is not None:
            # Remove existing tag assignments
            instance.tag_assignments.all().delete()
            # Assign new tags
            self._assign_tags(instance, tag_ids)
        
        return instance
    
    def _assign_tags(self, contact, tag_ids):
        """Helper method to assign tags to a contact"""
        if not tag_ids:
            return
        
        user = self.context['request'].user
        for tag_id in tag_ids:
            try:
                tag = ContactTag.objects.get(id=tag_id)
                ContactTagAssignment.objects.get_or_create(
                    contact=contact,
                    tag=tag,
                    defaults={'assigned_by': user}
                )
            except ContactTag.DoesNotExist:
                # Skip invalid tag IDs
                continue
