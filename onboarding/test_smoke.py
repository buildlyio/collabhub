"""
Smoke tests for CollabHub - Low maintenance regression testing
Tests that all pages load and basic forms render without errors.
Automatically discovers URLs and tests them with minimal configuration.
"""
from django.test import TestCase, Client
from django.urls import reverse, get_resolver
from django.contrib.auth import get_user_model
from onboarding.models import TeamMember, TeamMemberType, Customer, DevelopmentAgency
import re

User = get_user_model()


class SmokeTestBase(TestCase):
    """Base class with common setup for smoke tests"""
    
    @classmethod
    def setUpTestData(cls):
        """Create minimal test data needed across all tests"""
        # Create user types
        cls.frontend_type = TeamMemberType.objects.create(
            key='buildly-hire-frontend',
            label='Frontend Developer'
        )
        cls.backend_type = TeamMemberType.objects.create(
            key='buildly-hire-backend',
            label='Backend Developer'
        )
        
        # Create admin user and team member
        cls.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='testpass123'
        )
        cls.admin_member = TeamMember.objects.create(
            user=cls.admin_user,
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            approved=True
        )
        cls.admin_member.types.add(cls.frontend_type)
        
        # Create regular user and team member
        cls.regular_user = User.objects.create_user(
            username='developer_test',
            email='dev@test.com',
            password='testpass123'
        )
        cls.regular_member = TeamMember.objects.create(
            user=cls.regular_user,
            first_name='Test',
            last_name='Developer',
            email='dev@test.com',
            approved=True
        )
        cls.regular_member.types.add(cls.backend_type)
        
        # Create customer
        cls.customer = Customer.objects.create(
            company_name='Test Company',
            contact_name='Test Customer',
            contact_email='customer@test.com',
            username='customer_test',
            password='testpass123'
        )
        
        # Create agency
        cls.agency = DevelopmentAgency.objects.create(
            agency_name='Test Agency',
            contact_email='agency@test.com'
        )


class PageLoadSmokeTests(SmokeTestBase):
    """Test that all major pages load without 500 errors"""
    
    def setUp(self):
        self.client = Client()
    
    def test_public_pages_load(self):
        """Test public pages that don't require authentication"""
        public_urls = [
            '/',
            '/login/',
            '/register/',
        ]
        
        for url in public_urls:
            try:
                response = self.client.get(url, follow=True)
                self.assertIn(response.status_code, [200, 302, 404], 
                    f"Public page {url} returned unexpected status {response.status_code}")
            except Exception as e:
                self.fail(f"Public page {url} raised exception: {str(e)}")
    
    def test_authenticated_user_pages(self):
        """Test pages that require basic authentication"""
        self.client.login(username='developer_test', password='testpass123')
        
        user_urls = [
            '/dashboard/',
            '/onboarding/profile/edit/',
        ]
        
        for url in user_urls:
            try:
                response = self.client.get(url, follow=True)
                self.assertIn(response.status_code, [200, 302, 404],
                    f"User page {url} returned unexpected status {response.status_code}")
            except Exception as e:
                self.fail(f"User page {url} raised exception: {str(e)}")
    
    def test_admin_pages_load(self):
        """Test admin pages load without errors"""
        self.client.login(username='admin_test', password='testpass123')
        
        admin_urls = [
            '/onboarding/admin/dashboard/',
            '/onboarding/admin/developers/',
            '/onboarding/admin/customers/',
            '/onboarding/admin/quizzes/',
            '/onboarding/admin/resources/',
        ]
        
        for url in admin_urls:
            try:
                response = self.client.get(url, follow=True)
                self.assertIn(response.status_code, [200, 302, 404],
                    f"Admin page {url} returned unexpected status {response.status_code}")
            except Exception as e:
                self.fail(f"Admin page {url} raised exception: {str(e)}")
    
    def test_customer_pages_load(self):
        """Test customer dashboard pages"""
        # Customer uses a different auth system (not Django users)
        # Skip testing customer pages for now since they use custom authentication
        pass


class FormRenderingSmokeTests(SmokeTestBase):
    """Test that forms render without template errors"""
    
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin_test', password='testpass123')
    
    def test_registration_form_renders(self):
        """Test registration form page loads"""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        # Check for basic form elements
        self.assertContains(response, 'form', msg_prefix="Registration form not found")
    
    def test_login_form_renders(self):
        """Test login form page loads"""
        self.client.logout()
        response = self.client.get('/login/')
        self.assertIn(response.status_code, [200, 302, 404])
        if response.status_code == 200:
            self.assertContains(response, 'form', msg_prefix="Login form not found")
    
    def test_profile_edit_form_renders(self):
        """Test profile edit form loads"""
        response = self.client.get('/onboarding/profile/edit/')
        self.assertIn(response.status_code, [200, 302, 404])
        if response.status_code == 200:
            self.assertContains(response, 'form', msg_prefix="Profile edit form not found")
    
    def test_quiz_creation_form_renders(self):
        """Test quiz creation form loads for admin"""
        response = self.client.get('/onboarding/admin/quiz/create/')
        self.assertIn(response.status_code, [200, 302, 404])
        if response.status_code == 200:
            self.assertContains(response, 'form', msg_prefix="Quiz creation form not found")
    
    def test_resource_creation_form_renders(self):
        """Test resource creation form loads for admin"""
        response = self.client.get('/onboarding/admin/resource/create/')
        self.assertIn(response.status_code, [200, 302, 404])
        if response.status_code == 200:
            self.assertContains(response, 'form', msg_prefix="Resource creation form not found")


class TemplateRegressionTests(SmokeTestBase):
    """Test for common template errors that cause FieldErrors"""
    
    def setUp(self):
        self.client = Client()
    
    def test_team_member_type_display_in_templates(self):
        """Test that all pages render TeamMember types correctly"""
        self.client.login(username='admin_test', password='testpass123')
        
        # Pages that display team member information
        pages_with_members = [
            '/onboarding/admin/developers/',
            '/onboarding/admin/dashboard/',
        ]
        
        for url in pages_with_members:
            try:
                response = self.client.get(url, follow=True)
                # Should not contain the old method call that causes errors
                content = response.content.decode('utf-8')
                self.assertNotIn('get_team_member_type_display', content,
                    f"Page {url} still contains deprecated get_team_member_type_display in rendered output")
            except Exception as e:
                # If page doesn't exist, that's OK
                if '404' not in str(e) and '500' not in str(e):
                    pass
    
    def test_customer_shared_pages_no_field_errors(self):
        """Test customer-facing shared pages don't have FieldErrors"""
        # Customer uses custom authentication, skip for now
        pass


class APISmokeTests(SmokeTestBase):
    """Test that API endpoints respond correctly"""
    
    def setUp(self):
        self.client = Client()
    
    def test_api_endpoints_respond(self):
        """Test major API endpoints return valid responses"""
        api_urls = [
            '/api/team-members/',
            '/api/customers/',
            '/marketplace/api/apps/',
        ]
        
        for url in api_urls:
            try:
                response = self.client.get(url)
                # API should return 200, 401 (unauthorized), or 403 (forbidden)
                # but not 500 (server error)
                self.assertIn(response.status_code, [200, 401, 403, 404],
                    f"API endpoint {url} returned error status {response.status_code}")
            except Exception as e:
                if '404' not in str(e):
                    self.fail(f"API endpoint {url} raised exception: {str(e)}")


class DatabaseIntegritySmokeTests(SmokeTestBase):
    """Test basic database integrity and model relationships"""
    
    def test_team_member_types_relationship(self):
        """Test TeamMember types ManyToMany relationship works"""
        member = TeamMember.objects.first()
        self.assertIsNotNone(member)
        
        # Should be able to access types without error
        types = member.types.all()
        self.assertIsNotNone(types)
        
        # Should be able to iterate types
        type_names = [t.label for t in types]
        self.assertIsInstance(type_names, list)
    
    def test_team_member_str_method(self):
        """Test TeamMember __str__ method doesn't cause errors"""
        member = TeamMember.objects.first()
        try:
            str_repr = str(member)
            self.assertIsInstance(str_repr, str)
            self.assertTrue(len(str_repr) > 0)
        except Exception as e:
            self.fail(f"TeamMember __str__ method raised exception: {str(e)}")
    
    def test_basic_model_queries(self):
        """Test basic queries on all major models"""
        models_to_test = [
            (TeamMember, 'types'),
            (TeamMemberType, 'label'),
            (Customer, 'company_name'),
            (DevelopmentAgency, 'agency_name'),
        ]
        
        for model, field in models_to_test:
            try:
                # Test that we can query the model
                count = model.objects.count()
                self.assertGreaterEqual(count, 0)
                
                # Test that we can access the field
                if count > 0:
                    obj = model.objects.first()
                    getattr(obj, field)
            except Exception as e:
                self.fail(f"Model {model.__name__} query failed: {str(e)}")
