"""
Serializers for opportunities app.
"""
from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import SalesStage, Opportunity, OpportunityHistory
from apps.contacts.models import Contact, Company
from apps.users.models import CustomUser


class SalesStageSerializer(serializers.ModelSerializer):
    """
    Serializer for SalesStage model.
    """
    opportunities_count = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = SalesStage
        fields = [
            'id', 'name', 'description', 'order', 'probability',
            'is_closed_won', 'is_closed_lost', 'is_active', 'color',
            'opportunities_count', 'total_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Custom validation for sales stages."""
        # Ensure closed stages have correct probabilities
        if data.get('is_closed_won'):
            data['probability'] = Decimal('100.00')
        elif data.get('is_closed_lost'):
            data['probability'] = Decimal('0.00')
        
        # Can't be both closed won and closed lost
        if data.get('is_closed_won') and data.get('is_closed_lost'):
            raise serializers.ValidationError(
                "Stage cannot be both closed won and closed lost."
            )
        
        return data


class SalesStageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating sales stages.
    """
    
    class Meta:
        model = SalesStage
        fields = [
            'name', 'description', 'order', 'probability',
            'is_closed_won', 'is_closed_lost', 'color'
        ]

    def validate_probability(self, value):
        """Validate probability is between 0 and 100."""
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Probability must be between 0 and 100."
            )
        return value


class ContactBasicSerializer(serializers.ModelSerializer):
    """
    Basic contact info for opportunity serialization.
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'job_title']


class CompanyBasicSerializer(serializers.ModelSerializer):
    """
    Basic company info for opportunity serialization.
    """
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'industry', 'website']


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user info for opportunity serialization.
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email']


class OpportunitySerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Opportunity model.
    """
    # Nested relationships for display
    contact = ContactBasicSerializer(read_only=True)
    company = CompanyBasicSerializer(read_only=True)
    stage = SalesStageSerializer(read_only=True)
    owner = UserBasicSerializer(read_only=True)
    
    # Computed fields
    weighted_value = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    days_in_stage = serializers.IntegerField(read_only=True)
    age_days = serializers.IntegerField(read_only=True)
    
    # Display fields
    priority_display = serializers.CharField(
        source='get_priority_display', 
        read_only=True
    )
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'description', 'value', 'contact', 'company', 
            'stage', 'owner', 'priority', 'priority_display', 'probability',
            'expected_close_date', 'actual_close_date', 'lead_source', 
            'notes', 'weighted_value', 'is_overdue', 'days_in_stage', 
            'age_days', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'weighted_value', 'is_overdue', 'days_in_stage', 
            'age_days', 'created_at', 'updated_at'
        ]


class OpportunityCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating opportunities.
    """
    # Use IDs for creation/updates
    contact_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    stage_id = serializers.IntegerField(write_only=True)
    owner_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Opportunity
        fields = [
            'name', 'description', 'value', 'contact_id', 'company_id',
            'stage_id', 'owner_id', 'priority', 'probability',
            'expected_close_date', 'lead_source', 'notes'
        ]

    def validate_contact_id(self, value):
        """Validate contact exists and belongs to current tenant."""
        try:
            contact = Contact.objects.get(id=value)
            return value
        except Contact.DoesNotExist:
            raise serializers.ValidationError("Contact does not exist.")

    def validate_company_id(self, value):
        """Validate company exists and belongs to current tenant."""
        if value is None:
            return value
        try:
            company = Company.objects.get(id=value)
            return value
        except Company.DoesNotExist:
            raise serializers.ValidationError("Company does not exist.")

    def validate_stage_id(self, value):
        """Validate stage exists and is active."""
        try:
            stage = SalesStage.objects.get(id=value, is_active=True)
            return value
        except SalesStage.DoesNotExist:
            raise serializers.ValidationError("Sales stage does not exist or is inactive.")

    def validate_owner_id(self, value):
        """Validate owner exists and belongs to current tenant."""
        try:
            user = CustomUser.objects.get(id=value, is_active=True)
            return value
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist or is inactive.")

    def validate_value(self, value):
        """Validate opportunity value is positive."""
        if value < 0:
            raise serializers.ValidationError("Opportunity value cannot be negative.")
        return value

    def validate_probability(self, value):
        """Validate probability is between 0 and 100."""
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Probability must be between 0 and 100.")
        return value

    def validate_expected_close_date(self, value):
        """Validate expected close date is not in the past."""
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "Expected close date cannot be in the past."
            )
        return value
    
    def get_tenant_user(self, request):
        try:
            return CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return None

    def create(self, validated_data):
        """Create opportunity with proper relationships."""
        # Extract IDs and get actual objects
        contact_id = validated_data.pop('contact_id')
        company_id = validated_data.pop('company_id', None)
        stage_id = validated_data.pop('stage_id')
        owner_id = validated_data.pop('owner_id')
        
        contact = Contact.objects.get(id=contact_id)
        company = Company.objects.get(id=company_id) if company_id else None
        stage = SalesStage.objects.get(id=stage_id)
        owner = CustomUser.objects.get(id=owner_id)
        
        # Create opportunity
        tenant_user = self.get_tenant_user(self.context['request'])
        opportunity = Opportunity.objects.create(
            contact=contact,
            company=company,
            stage=stage,
            owner=owner,
            created_by=tenant_user,
            **validated_data
        )
        
        # Create initial history entry
        OpportunityHistory.objects.create(
            opportunity=opportunity,
            action='created',
            new_stage=stage,
            new_value=opportunity.value,
            new_probability=opportunity.probability,
            changed_by=tenant_user,
            notes=f"Opportunity created in stage: {stage.name}"
        )
        
        return opportunity

    def update(self, instance, validated_data):
        """Update opportunity with history tracking."""
        # Track changes for history
        old_stage = instance.stage
        old_value = instance.value
        old_probability = instance.probability
        
        # Extract IDs and get actual objects
        if 'contact_id' in validated_data:
            contact_id = validated_data.pop('contact_id')
            validated_data['contact'] = Contact.objects.get(id=contact_id)
        
        if 'company_id' in validated_data:
            company_id = validated_data.pop('company_id')
            validated_data['company'] = Company.objects.get(id=company_id) if company_id else None
        
        if 'stage_id' in validated_data:
            stage_id = validated_data.pop('stage_id')
            validated_data['stage'] = SalesStage.objects.get(id=stage_id)
        
        if 'owner_id' in validated_data:
            owner_id = validated_data.pop('owner_id')
            validated_data['owner'] = CustomUser.objects.get(id=owner_id)
        
        # Update the instance
        validated_data['updated_by'] = self.context['request'].user
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        # Create history entries for significant changes
        user = self.context['request'].user
        
        if old_stage != instance.stage:
            OpportunityHistory.objects.create(
                opportunity=instance,
                action='stage_changed',
                old_stage=old_stage,
                new_stage=instance.stage,
                old_probability=old_probability,
                new_probability=instance.probability,
                changed_by=user,
                notes=f"Stage changed from {old_stage} to {instance.stage}"
            )
        
        if old_value != instance.value:
            OpportunityHistory.objects.create(
                opportunity=instance,
                action='value_changed',
                old_value=old_value,
                new_value=instance.value,
                changed_by=user,
                notes=f"Value changed from {old_value} to {instance.value}"
            )
        
        return instance


class OpportunityHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for opportunity history.
    """
    changed_by = UserBasicSerializer(read_only=True)
    old_stage = SalesStageSerializer(read_only=True)
    new_stage = SalesStageSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = OpportunityHistory
        fields = [
            'id', 'action', 'action_display', 'old_stage', 'new_stage',
            'old_value', 'new_value', 'old_probability', 'new_probability',
            'notes', 'changed_by', 'created_at'
        ]


class OpportunityStageChangeSerializer(serializers.Serializer):
    """
    Serializer for changing opportunity stage.
    """
    stage_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_stage_id(self, value):
        """Validate stage exists and is active."""
        try:
            stage = SalesStage.objects.get(id=value, is_active=True)
            return value
        except SalesStage.DoesNotExist:
            raise serializers.ValidationError("Sales stage does not exist or is inactive.")


class PipelineAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for pipeline analytics data.
    """
    total_opportunities = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_weighted_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_deal_size = serializers.DecimalField(max_digits=12, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_sales_cycle = serializers.IntegerField()  # days
    
    stages = serializers.ListField(
        child=serializers.DictField()
    )
    
    monthly_performance = serializers.ListField(
        child=serializers.DictField()
    )