"""
Tests for demo app.
Tests DemoRequest model and functionality.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.demo.models import DemoRequest


class DemoRequestModelTest(TestCase):
    """Test DemoRequest model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.demo_data = {
            'company_name': 'Test Corporation',
            'email': 'admin@testcorp.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'message': 'We would like to try your product.',
            'industry': 'Technology',
            'company_size': '11-50'
        }
    
    def test_create_demo_request(self):
        """Test creating a demo request."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        self.assertEqual(demo.company_name, 'Test Corporation')
        self.assertEqual(demo.email, 'admin@testcorp.com')
        self.assertEqual(demo.first_name, 'John')
        self.assertEqual(demo.last_name, 'Doe')
        self.assertEqual(demo.status, 'pending')
        self.assertTrue(demo.created_at)
    
    def test_demo_request_str_representation(self):
        """Test string representation of DemoRequest."""
        demo = DemoRequest.objects.create(**self.demo_data)
        expected = f"{demo.company_name} - {demo.first_name} {demo.last_name} ({demo.status})"
        self.assertEqual(str(demo), expected)
    
    def test_demo_request_status_choices(self):
        """Test demo request status choices."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        # Test valid status updates
        valid_statuses = ['pending', 'processing', 'approved', 'converted', 'failed', 'rejected']
        for status in valid_statuses:
            demo.status = status
            demo.save()
            demo.refresh_from_db()
            self.assertEqual(demo.status, status)
    
    def test_email_validation(self):
        """Test email validation."""
        demo_data = self.demo_data.copy()
        demo_data['email'] = 'invalid-email'
        
        demo = DemoRequest(**demo_data)
        with self.assertRaises(ValidationError):
            demo.full_clean()
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        required_fields = ['company_name', 'email', 'first_name', 'last_name']
        
        for field in required_fields:
            demo_data = self.demo_data.copy()
            demo_data[field] = ''
            
            demo = DemoRequest(**demo_data)
            with self.assertRaises(ValidationError):
                demo.full_clean()
    
    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        demo_data = {
            'company_name': 'Test Corp',
            'email': 'test@testcorp.com',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        
        demo = DemoRequest.objects.create(**demo_data)
        self.assertEqual(demo.phone, '')
        self.assertEqual(demo.message, '')
    
    def test_demo_request_ordering(self):
        """Test demo request default ordering."""
        demo1 = DemoRequest.objects.create(
            company_name='A Company',
            email='a@company.com',
            first_name='Alice',
            last_name='Smith'
        )
        demo2 = DemoRequest.objects.create(
            company_name='B Company', 
            email='b@company.com',
            first_name='Bob',
            last_name='Jones'
        )
        
        # Should be ordered by created_at descending (newest first)
        demos = list(DemoRequest.objects.all())
        self.assertEqual(demos[0], demo2)  # Most recent first
        self.assertEqual(demos[1], demo1)
    
    def test_status_update(self):
        """Test updating demo request status."""
        demo = DemoRequest.objects.create(**self.demo_data)
        original_status = demo.status
        
        demo.status = 'approved'
        demo.save()
        
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'approved')
        self.assertNotEqual(demo.status, original_status)
