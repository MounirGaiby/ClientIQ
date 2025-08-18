"""
Views for demo app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings

from .models import DemoRequest
from .serializers import (
    DemoRequestSerializer,
    DemoRequestCreateSerializer,
    DemoRequestAdminSerializer
)


class DemoRequestListCreateView(generics.ListCreateAPIView):
    """
    List all demo requests or create a new one.
    """
    queryset = DemoRequest.objects.all()
    permission_classes = [AllowAny]  # Allow public access for demo requests
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DemoRequestCreateSerializer
        return DemoRequestSerializer
    
    def perform_create(self, serializer):
        """
        Create a new demo request and send notification email.
        """
        demo_request = serializer.save()
        
        # Send notification email (in production, use Celery for async)
        try:
            send_mail(
                subject=f'New Demo Request from {demo_request.company_name}',
                message=f"""
                New demo request received:
                
                Company: {demo_request.company_name}
                Contact: {demo_request.first_name} {demo_request.last_name}
                Email: {demo_request.email}
                Phone: {demo_request.phone}
                Job Title: {demo_request.job_title}
                Company Size: {demo_request.company_size}
                Industry: {demo_request.industry}
                Message: {demo_request.message}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['admin@clientiq.com'],  # Configure admin email
                fail_silently=True,
            )
            
            # Send confirmation email to requester
            send_mail(
                subject='Demo Request Received - ClientIQ',
                message=f"""
                Dear {demo_request.first_name},
                
                Thank you for your interest in ClientIQ. We have received your demo request 
                and will review it shortly. You will receive an email with next steps within 
                24 hours.
                
                Best regards,
                The ClientIQ Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[demo_request.email],
                fail_silently=True,
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Email sending failed: {e}")


class DemoRequestDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a demo request (admin only).
    """
    queryset = DemoRequest.objects.all()
    serializer_class = DemoRequestAdminSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for admin access
