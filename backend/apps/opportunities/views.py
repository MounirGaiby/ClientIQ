"""
API views for opportunities app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Avg, Count, F, Case, When, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.users.models import CustomUser

from .models import SalesStage, Opportunity, OpportunityHistory
from .serializers import (
    SalesStageSerializer,
    SalesStageCreateSerializer,
    OpportunitySerializer,
    OpportunityCreateUpdateSerializer,
    OpportunityHistorySerializer,
    OpportunityStageChangeSerializer,
    PipelineAnalyticsSerializer
)


class SalesStageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales stages.
    
    Provides CRUD operations for sales pipeline stages.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'name', 'probability']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        """Get sales stages with opportunity counts and values."""
        return SalesStage.objects.annotate(
            opportunities_count=Count('opportunities'),
            total_value=Coalesce(
                Sum('opportunities__value'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return SalesStageCreateSerializer
        return SalesStageSerializer
    
    def get_tenant_user(self, request):
        try:
            return CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return None
    
    def perform_create(self, serializer):
        """Set created_by when creating a stage."""
        tenant_user = self.get_tenant_user(self.request)
        serializer.save(created_by=tenant_user)
    
    @action(detail=False, methods=['post'])
    def create_default_stages(self, request):
        """
        Create default sales stages for a new tenant.
        """
        default_stages = [
            {
                'name': 'Lead',
                'description': 'Initial contact, unqualified lead',
                'order': 1,
                'probability': 10,
                'color': '#64748b'
            },
            {
                'name': 'Qualified',
                'description': 'Lead has been qualified and shows interest',
                'order': 2,
                'probability': 25,
                'color': '#3b82f6'
            },
            {
                'name': 'Proposal',
                'description': 'Proposal or quote has been sent',
                'order': 3,
                'probability': 50,
                'color': '#8b5cf6'
            },
            {
                'name': 'Negotiation',
                'description': 'In active negotiation phase',
                'order': 4,
                'probability': 75,
                'color': '#f59e0b'
            },
            {
                'name': 'Closed Won',
                'description': 'Deal successfully closed',
                'order': 5,
                'probability': 100,
                'color': '#10b981',
                'is_closed_won': True
            },
            {
                'name': 'Closed Lost',
                'description': 'Deal was lost or cancelled',
                'order': 6,
                'probability': 0,
                'color': '#ef4444',
                'is_closed_lost': True
            }
        ]
        
        created_stages = []
        for stage_data in default_stages:
            tenant_user = self.get_tenant_user(self.request)
            stage, created = SalesStage.objects.get_or_create(
                name=stage_data['name'],
                defaults={**stage_data, 'created_by': tenant_user}
            )
            if created:
                created_stages.append(stage)
        
        serializer = SalesStageSerializer(created_stages, many=True)
        return Response({
            'message': f'Created {len(created_stages)} default stages',
            'stages': serializer.data
        }, status=status.HTTP_201_CREATED)


class OpportunityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing opportunities.
    
    Provides full CRUD operations plus additional actions for
    stage management and analytics.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'owner', 'priority', 'contact', 'company']
    search_fields = ['name', 'description', 'contact__first_name', 'contact__last_name', 'company__name']
    ordering_fields = ['name', 'value', 'probability', 'expected_close_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get opportunities with related data and computed fields."""
        queryset = Opportunity.objects.select_related(
            'contact', 'company', 'stage', 'owner', 'created_by'
        )
        # REMOVED the .annotate() that was causing the conflict
        # The weighted_value is already provided by the model's @property
        
        # Filter by query parameters
        stage_id = self.request.query_params.get('stage_id')
        if stage_id:
            queryset = queryset.filter(stage_id=stage_id)
        
        owner_id = self.request.query_params.get('owner_id')
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        
        # Filter by date ranges
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Filter by expected close date
        close_start = self.request.query_params.get('close_start')
        close_end = self.request.query_params.get('close_end')
        if close_start:
            queryset = queryset.filter(expected_close_date__gte=close_start)
        if close_end:
            queryset = queryset.filter(expected_close_date__lte=close_end)
        
        # Filter overdue opportunities
        if self.request.query_params.get('overdue') == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                expected_close_date__lt=today,
                stage__is_closed=False
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return OpportunityCreateUpdateSerializer
        return OpportunitySerializer
    
    # def perform_create(self, serializer):
    #     """Set created_by when creating an opportunity."""
    #     serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def change_stage(self, request, pk=None):
        """
        Change opportunity stage with history tracking.
        """
        opportunity = self.get_object()
        serializer = OpportunityStageChangeSerializer(data=request.data)
        
        if serializer.is_valid():
            stage_id = serializer.validated_data['stage_id']
            notes = serializer.validated_data.get('notes', '')
            
            try:
                new_stage = SalesStage.objects.get(id=stage_id, is_active=True)
                opportunity.move_to_stage(new_stage, None, notes)
                
                # Return updated opportunity
                response_serializer = OpportunitySerializer(opportunity)
                return Response({
                    'message': f'Opportunity moved to {new_stage.name}',
                    'opportunity': response_serializer.data
                })
            except SalesStage.DoesNotExist:
                return Response(
                    {'error': 'Sales stage not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Get opportunity history.
        """
        opportunity = self.get_object()
        history = OpportunityHistory.objects.filter(
            opportunity=opportunity
        ).select_related('changed_by', 'old_stage', 'new_stage')
        
        serializer = OpportunityHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """
        Get pipeline view of opportunities grouped by stage.
        """
        # Get all active stages with their opportunities
        stages = SalesStage.objects.filter(is_active=True).prefetch_related(
            'opportunities'
        ).annotate(
            opportunities_count=Count('opportunities'),
            total_value=Coalesce(
                Sum('opportunities__value'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
            # REMOVED weighted_value annotation - will be calculated by the model property
        ).order_by('order')
        
        pipeline_data = []
        for stage in stages:
            opportunities = stage.opportunities.select_related('contact', 'company', 'owner')
            opportunity_serializer = OpportunitySerializer(opportunities, many=True)
            
            # Calculate weighted_value manually from the opportunities
            stage_weighted_value = sum(
                opp.weighted_value for opp in opportunities
            ) if opportunities else Decimal('0.00')
            
            pipeline_data.append({
                'stage': SalesStageSerializer(stage).data,
                'opportunities': opportunity_serializer.data,
                'summary': {
                    'count': stage.opportunities_count,
                    'total_value': stage.total_value,
                    'weighted_value': stage_weighted_value
                }
            })
        
        # Calculate totals
        total_weighted_value = sum(
            stage_data['summary']['weighted_value'] for stage_data in pipeline_data
        )
        
        return Response({
            'pipeline': pipeline_data,
            'total_opportunities': sum(stage.opportunities_count for stage in stages),
            'total_pipeline_value': sum(stage.total_value for stage in stages),
            'total_weighted_value': total_weighted_value
        })
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get pipeline analytics and performance metrics.
        """
        # Date range for analysis (default: last 12 months)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        # Override with query params if provided
        if request.query_params.get('start_date'):
            start_date = datetime.strptime(request.query_params['start_date'], '%Y-%m-%d').date()
        if request.query_params.get('end_date'):
            end_date = datetime.strptime(request.query_params['end_date'], '%Y-%m-%d').date()
        
        # Basic metrics
        opportunities = Opportunity.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        
        total_opportunities = opportunities.count()
        total_value = opportunities.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
        total_weighted_value = opportunities.aggregate(
            weighted=Sum(F('value') * F('probability') / 100)
        )['weighted'] or Decimal('0.00')
        
        # Closed deals metrics
        closed_won = opportunities.filter(stage__is_closed_won=True)
        closed_lost = opportunities.filter(stage__is_closed_lost=True)
        
        won_count = closed_won.count()
        lost_count = closed_lost.count()
        closed_count = won_count + lost_count
        
        conversion_rate = (won_count / closed_count * 100) if closed_count > 0 else 0
        average_deal_size = (closed_won.aggregate(Avg('value'))['value__avg'] or Decimal('0.00'))
        
        # Average sales cycle (days from creation to close)
        closed_opportunities = opportunities.filter(
            actual_close_date__isnull=False
        ).annotate(
            sales_cycle=F('actual_close_date') - F('created_at__date')
        )
        
        avg_sales_cycle = 0
        if closed_opportunities.exists():
            cycles = [opp.sales_cycle.days for opp in closed_opportunities]
            avg_sales_cycle = sum(cycles) / len(cycles) if cycles else 0
        
        # Stage analysis
        stages_data = []
        for stage in SalesStage.objects.filter(is_active=True).order_by('order'):
            stage_opps = opportunities.filter(stage=stage)
            stages_data.append({
                'stage_name': stage.name,
                'stage_id': stage.id,
                'count': stage_opps.count(),
                'total_value': stage_opps.aggregate(Sum('value'))['value__sum'] or Decimal('0.00'),
                'average_value': stage_opps.aggregate(Avg('value'))['value__avg'] or Decimal('0.00'),
                'probability': stage.probability
            })
        
        # Monthly performance (last 12 months)
        monthly_data = []
        current_date = start_date
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            if current_date.month == 12:
                month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
            
            month_opps = opportunities.filter(
                created_at__date__range=[month_start, month_end]
            )
            month_won = month_opps.filter(stage__is_closed_won=True)
            
            monthly_data.append({
                'month': current_date.strftime('%Y-%m'),
                'month_name': current_date.strftime('%B %Y'),
                'opportunities_created': month_opps.count(),
                'opportunities_won': month_won.count(),
                'total_value': month_opps.aggregate(Sum('value'))['value__sum'] or Decimal('0.00'),
                'won_value': month_won.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        analytics_data = {
            'total_opportunities': total_opportunities,
            'total_value': total_value,
            'total_weighted_value': total_weighted_value,
            'average_deal_size': average_deal_size,
            'conversion_rate': Decimal(str(conversion_rate)),
            'average_sales_cycle': int(avg_sales_cycle),
            'stages': stages_data,
            'monthly_performance': monthly_data
        }
        
        serializer = PipelineAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_opportunities(self, request):
        """
        Get opportunities assigned to the current user.
        """
        opportunities = self.get_queryset().filter(owner=request.user)
        
        # Apply additional filters
        stage = request.query_params.get('stage')
        if stage:
            opportunities = opportunities.filter(stage__name__icontains=stage)
        
        priority = request.query_params.get('priority')
        if priority:
            opportunities = opportunities.filter(priority=priority)
        
        serializer = OpportunitySerializer(opportunities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue opportunities (past expected close date).
        """
        today = timezone.now().date()
        overdue_opps = self.get_queryset().filter(
            expected_close_date__lt=today,
            stage__is_closed=False
        ).order_by('expected_close_date')
        
        serializer = OpportunitySerializer(overdue_opps, many=True)
        return Response({
            'count': overdue_opps.count(),
            'opportunities': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def closing_soon(self, request):
        """
        Get opportunities closing within the next 30 days.
        """
        today = timezone.now().date()
        future_date = today + timedelta(days=30)
        
        closing_soon = self.get_queryset().filter(
            expected_close_date__range=[today, future_date],
            stage__is_closed=False
        ).order_by('expected_close_date')
        
        serializer = OpportunitySerializer(closing_soon, many=True)
        return Response({
            'count': closing_soon.count(),
            'opportunities': serializer.data
        })