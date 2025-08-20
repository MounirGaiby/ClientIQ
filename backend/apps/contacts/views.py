"""
Contact views for ClientIQ CRM.

Provides REST API endpoints for managing contacts, companies, and tags.
"""

from rest_framework import generics, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.db import transaction

from .models import Company, Contact, ContactTag, ContactTagAssignment, ContactType
from .serializers import (
    CompanySerializer, ContactListSerializer, ContactDetailSerializer,
    ContactCreateUpdateSerializer, ContactTagSerializer, ContactTagAssignmentSerializer
)


class CompanyViewSet(ModelViewSet):
    """ViewSet for Company CRUD operations"""
    
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['industry', 'size', 'country']
    search_fields = ['name', 'website', 'industry', 'city', 'country']
    ordering_fields = ['name', 'industry', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Return companies for current tenant"""
        return Company.objects.all()
    
    def perform_create(self, serializer):
        """Set created_by when creating a company"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating a company"""
        serializer.save(updated_by=self.request.user)


class ContactTagViewSet(ModelViewSet):
    """ViewSet for ContactTag CRUD operations"""
    
    serializer_class = ContactTagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Return tags for current tenant"""
        return ContactTag.objects.annotate(
            contact_count=Count('contact_assignments')
        )
    
    def perform_create(self, serializer):
        """Set created_by when creating a tag"""
        serializer.save(created_by=self.request.user)


class ContactViewSet(ModelViewSet):
    """ViewSet for Contact CRUD operations with advanced filtering"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contact_type', 'is_active', 'company', 'owner']
    search_fields = ['first_name', 'last_name', 'email', 'company__name', 'job_title']
    ordering_fields = ['last_name', 'first_name', 'email', 'score', 'created_at']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        """Return contacts for current tenant with related data"""
        queryset = Contact.objects.select_related('company', 'owner', 'created_by', 'updated_by')
        
        # Filter by score range
        min_score = self.request.query_params.get('min_score')
        max_score = self.request.query_params.get('max_score')
        
        if min_score is not None:
            try:
                queryset = queryset.filter(score__gte=int(min_score))
            except ValueError:
                pass
        
        if max_score is not None:
            try:
                queryset = queryset.filter(score__lte=int(max_score))
            except ValueError:
                pass
        
        # Filter by tag
        tag_ids = self.request.query_params.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tag_assignments__tag__id__in=tag_ids).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ContactListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ContactCreateUpdateSerializer
        else:
            return ContactDetailSerializer
    
    def perform_create(self, serializer):
        """Set created_by when creating a contact"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating a contact"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_score(self, request, pk=None):
        """Update contact score with delta value"""
        contact = self.get_object()
        
        try:
            delta = int(request.data.get('delta', 0))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid delta value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contact.update_score(delta)
        
        return Response({
            'score': contact.score,
            'score_level': contact.get_score_level()
        })
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """Add a tag to the contact"""
        contact = self.get_object()
        
        try:
            tag_id = int(request.data.get('tag_id'))
            tag = ContactTag.objects.get(id=tag_id)
        except (ValueError, TypeError, ContactTag.DoesNotExist):
            return Response(
                {'error': 'Invalid tag ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment, created = ContactTagAssignment.objects.get_or_create(
            contact=contact,
            tag=tag,
            defaults={'assigned_by': request.user}
        )
        
        if created:
            return Response({'message': 'Tag added successfully'})
        else:
            return Response(
                {'message': 'Tag already assigned'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def remove_tag(self, request, pk=None):
        """Remove a tag from the contact"""
        contact = self.get_object()
        
        try:
            tag_id = int(request.data.get('tag_id'))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid tag ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = ContactTagAssignment.objects.filter(
            contact=contact,
            tag_id=tag_id
        ).delete()
        
        if deleted_count > 0:
            return Response({'message': 'Tag removed successfully'})
        else:
            return Response(
                {'message': 'Tag not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get contact statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_contacts': queryset.count(),
            'active_contacts': queryset.filter(is_active=True).count(),
            'by_type': {},
            'by_score_level': {}
        }
        
        # Statistics by contact type
        for contact_type, display_name in ContactType.choices:
            count = queryset.filter(contact_type=contact_type).count()
            stats['by_type'][contact_type] = {
                'count': count,
                'display_name': display_name
            }
        
        # Statistics by score level
        for level, min_score, max_score in [
            ('Hot', 80, 100),
            ('Warm', 60, 79),
            ('Cold', 40, 59),
            ('Unqualified', 0, 39)
        ]:
            count = queryset.filter(score__gte=min_score, score__lte=max_score).count()
            stats['by_score_level'][level.lower()] = count
        
        return Response(stats)


# Legacy function-based views for simpler endpoints
class ContactListCreateView(generics.ListCreateAPIView):
    """Simple list and create view for contacts"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['contact_type', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']
    
    def get_queryset(self):
        return Contact.objects.select_related('company')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactCreateUpdateSerializer
        return ContactListSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            owner=self.request.user
        )


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Simple detail view for contacts"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.select_related('company', 'owner')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContactCreateUpdateSerializer
        return ContactDetailSerializer
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
