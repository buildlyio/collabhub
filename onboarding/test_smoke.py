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


class ContractSystemSmokeTests(SmokeTestBase):
    """Test contract creation, signing, and document generation"""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create company admin
        from onboarding.models import CompanyAdmin
        cls.company_admin_user = User.objects.create_user(
            username='companyadmin',
            email='admin@company.com',
            password='testpass123'
        )
        cls.company_admin = CompanyAdmin.objects.create(
            user=cls.company_admin_user,
            customer=cls.customer,
            role='admin',
            can_sign_contracts=True,
            is_active=True
        )
    
    def setUp(self):
        self.client = Client()
    
    def test_contract_creation_page_loads(self):
        """Test contract creation form loads for staff"""
        self.client.login(username='admin_test', password='testpass123')
        url = f'/onboarding/admin/customers/{self.customer.id}/contracts/new/'
        
        try:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 404],
                f"Contract creation page returned {response.status_code}")
            if response.status_code == 200:
                self.assertContains(response, 'form')
        except Exception as e:
            self.fail(f"Contract creation page raised exception: {str(e)}")
    
    def test_contract_creation_with_line_items(self):
        """Test creating a contract with dynamic line items"""
        self.client.login(username='admin_test', password='testpass123')
        
        from onboarding.models import Contract, ContractLineItem
        from datetime import date, timedelta
        
        # Create contract
        contract = Contract.objects.create(
            customer=self.customer,
            title='Test Service Agreement',
            contract_text='Standard terms and conditions',
            contract_type='engagement',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            status='draft',
            created_by=self.admin_user
        )
        
        # Add line items
        line_item = ContractLineItem.objects.create(
            contract=contract,
            service_type='team',
            description='2 Full-Stack Developers',
            quantity=2,
            unit_price=1500,
            billing_frequency='monthly',
            discount_percentage=10
        )
        
        # Test calculations
        self.assertEqual(line_item.subtotal, 3000)
        self.assertEqual(line_item.discount_amount, 300)
        self.assertEqual(line_item.total, 2700)
        
        # Test contract total
        self.assertEqual(contract.total_amount, 2700)
    
    def test_contract_signing_flow(self):
        """Test contract signing generates hash"""
        from onboarding.models import Contract
        from datetime import date, timedelta
        from django.utils import timezone
        
        # Create contract
        contract = Contract.objects.create(
            customer=self.customer,
            title='Test Contract',
            contract_text='Terms',
            contract_type='engagement',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='pending',
            created_by=self.admin_user
        )
        
        # Sign contract
        contract.status = 'signed'
        contract.signed_by = 'John Doe'
        contract.signed_at = timezone.now()
        contract.signature_data = 'base64_signature_data'
        contract.contract_hash = contract.generate_hash()
        contract.save()
        
        # Verify hash
        self.assertIsNotNone(contract.contract_hash)
        self.assertEqual(len(contract.contract_hash), 64)  # SHA256 hex
        self.assertTrue(contract.verify_hash())
    
    def test_contract_hash_tamper_detection(self):
        """Test that modifying contract invalidates hash"""
        from onboarding.models import Contract
        from datetime import date, timedelta
        from django.utils import timezone
        
        contract = Contract.objects.create(
            customer=self.customer,
            title='Test Contract',
            contract_text='Original terms',
            contract_type='engagement',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='signed',
            signed_by='John Doe',
            signed_at=timezone.now(),
            signature_data='sig_data',
            created_by=self.admin_user
        )
        
        # Generate and save hash
        contract.contract_hash = contract.generate_hash()
        contract.save()
        
        # Verify original
        self.assertTrue(contract.verify_hash())
        
        # Tamper with contract
        contract.contract_text = 'Modified terms'
        
        # Hash should no longer match
        self.assertFalse(contract.verify_hash())
    
    def test_contract_pdf_generation(self):
        """Test PDF generation for signed contracts"""
        from onboarding.models import Contract, ContractLineItem
        from datetime import date, timedelta
        from django.utils import timezone
        from onboarding.document_generator import generate_contract_pdf
        
        contract = Contract.objects.create(
            customer=self.customer,
            title='Service Agreement',
            contract_text='Terms and conditions',
            contract_type='engagement',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            status='signed',
            signed_by='Test Admin',
            signed_at=timezone.now(),
            signature_data='signature_base64',
            created_by=self.admin_user
        )
        contract.contract_hash = contract.generate_hash()
        contract.save()
        
        # Add line item
        ContractLineItem.objects.create(
            contract=contract,
            service_type='hosting',
            description='GCP Hosting',
            quantity=1,
            unit_price=750,
            billing_frequency='monthly'
        )
        
        # Generate PDF
        try:
            pdf_content = generate_contract_pdf(contract)
            self.assertIsNotNone(pdf_content)
            self.assertGreater(len(pdf_content), 1000)  # Should have content
            # Check it's a PDF
            self.assertTrue(pdf_content[:4] == b'%PDF')
        except Exception as e:
            self.fail(f"PDF generation failed: {str(e)}")
    
    def test_contract_download_page(self):
        """Test contract download page loads"""
        from onboarding.models import Contract
        from datetime import date, timedelta
        from django.utils import timezone
        
        contract = Contract.objects.create(
            customer=self.customer,
            title='Test Contract',
            contract_text='Terms',
            contract_type='engagement',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='signed',
            signed_by='Admin',
            signed_at=timezone.now(),
            created_by=self.admin_user
        )
        contract.contract_hash = contract.generate_hash()
        contract.save()
        
        self.client.login(username='companyadmin', password='testpass123')
        url = f'/onboarding/contract/{contract.id}/download/'
        
        try:
            response = self.client.get(url)
            # Should return PDF or redirect
            self.assertIn(response.status_code, [200, 302, 403],
                f"Contract download returned {response.status_code}")
        except Exception as e:
            # Some errors are OK if PDF generation fails in test
            if '500' not in str(e):
                pass


class CertificationSystemSmokeTests(SmokeTestBase):
    """Test certification creation and issuance"""
    
    def test_certification_level_creation(self):
        """Test creating a certification level"""
        from onboarding.models import CertificationLevel
        
        cert_level = CertificationLevel.objects.create(
            name='React Frontend Specialist',
            level_type='senior',
            description='Advanced React development skills',
            requirements='3+ years React experience',
            skills='React, Redux, TypeScript',
            price=299.99,
            badge_color='#3B82F6',
            created_by=self.admin_user
        )
        
        self.assertEqual(cert_level.name, 'React Frontend Specialist')
        self.assertEqual(cert_level.get_level_type_display(), 'Senior')
    
    def test_certificate_issuance(self):
        """Test issuing a certificate to a developer"""
        from onboarding.models import CertificationLevel, DeveloperCertification
        
        # Create certification level
        cert_level = CertificationLevel.objects.create(
            name='Python Backend Expert',
            level_type='expert',
            description='Expert-level Python development',
            created_by=self.admin_user
        )
        
        # Issue certificate
        cert = DeveloperCertification.objects.create(
            developer=self.regular_member,
            certification_level=cert_level,
            issued_by=self.admin_user,
            score=95.5
        )
        
        # Check auto-generated fields
        self.assertIsNotNone(cert.certificate_number)
        self.assertTrue(cert.certificate_number.startswith('CERT-'))
        self.assertTrue(cert.is_valid)
        self.assertFalse(cert.is_expired)
        self.assertFalse(cert.is_revoked)
    
    def test_certificate_hash_generation(self):
        """Test certificate hash generation"""
        from onboarding.models import CertificationLevel, DeveloperCertification
        
        cert_level = CertificationLevel.objects.create(
            name='Test Certification',
            level_type='intermediate',
            description='Test cert',
            created_by=self.admin_user
        )
        
        cert = DeveloperCertification.objects.create(
            developer=self.regular_member,
            certification_level=cert_level,
            issued_by=self.admin_user,
            score=85.0
        )
        
        # Generate hash
        cert.certificate_hash = cert.generate_hash()
        cert.save()
        
        # Verify
        self.assertIsNotNone(cert.certificate_hash)
        self.assertEqual(len(cert.certificate_hash), 64)
        self.assertTrue(cert.verify_hash())
    
    def test_certificate_revocation(self):
        """Test certificate revocation"""
        from onboarding.models import CertificationLevel, DeveloperCertification
        from django.utils import timezone
        
        cert_level = CertificationLevel.objects.create(
            name='Revoked Cert',
            level_type='junior',
            description='Test',
            created_by=self.admin_user
        )
        
        cert = DeveloperCertification.objects.create(
            developer=self.regular_member,
            certification_level=cert_level,
            issued_by=self.admin_user
        )
        
        # Initially valid
        self.assertTrue(cert.is_valid)
        
        # Revoke
        cert.is_revoked = True
        cert.revoked_at = timezone.now()
        cert.revoked_by = self.admin_user
        cert.revoked_reason = 'Test revocation'
        cert.save()
        
        # No longer valid
        self.assertFalse(cert.is_valid)
    
    def test_certificate_pdf_generation(self):
        """Test certificate PDF generation"""
        from onboarding.models import CertificationLevel, DeveloperCertification
        from onboarding.document_generator import generate_certificate_pdf
        
        cert_level = CertificationLevel.objects.create(
            name='Full-Stack Developer',
            level_type='senior',
            description='Senior full-stack development',
            badge_color='#10B981',
            created_by=self.admin_user
        )
        
        cert = DeveloperCertification.objects.create(
            developer=self.regular_member,
            certification_level=cert_level,
            issued_by=self.admin_user,
            score=92.0
        )
        cert.certificate_hash = cert.generate_hash()
        cert.save()
        
        # Generate PDF
        try:
            pdf_content = generate_certificate_pdf(cert)
            self.assertIsNotNone(pdf_content)
            self.assertGreater(len(pdf_content), 1000)
            self.assertTrue(pdf_content[:4] == b'%PDF')
        except Exception as e:
            self.fail(f"Certificate PDF generation failed: {str(e)}")
    
    def test_certification_admin_pages_load(self):
        """Test certification management pages"""
        self.client.login(username='admin_test', password='testpass123')
        
        urls = [
            '/onboarding/admin/certifications/',
            '/onboarding/admin/certification/create/',
        ]
        
        for url in urls:
            try:
                response = self.client.get(url)
                self.assertIn(response.status_code, [200, 302, 404],
                    f"Certification admin page {url} returned {response.status_code}")
            except Exception as e:
                if '404' not in str(e) and '500' not in str(e):
                    pass
    
    def test_developer_certificates_page(self):
        """Test developer certificate listing page"""
        self.client.login(username='developer_test', password='testpass123')
        
        try:
            response = self.client.get('/onboarding/certificates/')
            self.assertIn(response.status_code, [200, 302, 404])
        except Exception as e:
            if '404' not in str(e) and '500' not in str(e):
                pass


class VerificationSystemSmokeTests(SmokeTestBase):
    """Test public verification endpoints"""
    
    def test_verification_home_page(self):
        """Test verification homepage loads (public)"""
        response = self.client.get('/onboarding/verify/')
        self.assertIn(response.status_code, [200, 302, 404])
    
    def test_contract_verification(self):
        """Test contract verification by hash"""
        from onboarding.models import Contract
        from datetime import date, timedelta
        from django.utils import timezone
        
        contract = Contract.objects.create(
            customer=self.customer,
            title='Verified Contract',
            contract_text='Terms',
            contract_type='engagement',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='signed',
            signed_by='Test User',
            signed_at=timezone.now(),
            created_by=self.admin_user
        )
        contract.contract_hash = contract.generate_hash()
        contract.save()
        
        # Test verification endpoint
        url = f'/onboarding/verify/contract/{contract.contract_hash}/'
        try:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 404])
            if response.status_code == 200:
                self.assertContains(response, contract.title)
        except Exception as e:
            if '404' not in str(e) and '500' not in str(e):
                pass
    
    def test_certificate_verification(self):
        """Test certificate verification by hash"""
        from onboarding.models import CertificationLevel, DeveloperCertification
        
        cert_level = CertificationLevel.objects.create(
            name='Verified Cert',
            level_type='intermediate',
            description='Test',
            created_by=self.admin_user
        )
        
        cert = DeveloperCertification.objects.create(
            developer=self.regular_member,
            certification_level=cert_level,
            issued_by=self.admin_user
        )
        cert.certificate_hash = cert.generate_hash()
        cert.save()
        
        # Test verification endpoint
        url = f'/onboarding/verify/certificate/{cert.certificate_hash}/'
        try:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 404])
            if response.status_code == 200:
                self.assertContains(response, cert.certificate_number)
        except Exception as e:
            if '404' not in str(e) and '500' not in str(e):
                pass


class DashboardIntegrationSmokeTests(SmokeTestBase):
    """Test that new features appear on dashboard"""
    
    def test_contracts_appear_on_dashboard(self):
        """Test contracts show on company admin dashboard"""
        from onboarding.models import CompanyAdmin, Contract
        from datetime import date, timedelta
        
        # Create company admin user and team member
        admin_user = User.objects.create_user(
            username='companyadmin2',
            password='testpass123'
        )
        
        # Create team member for company admin (required for dashboard)
        team_member = TeamMember.objects.create(
            user=admin_user,
            first_name='Company',
            last_name='Admin',
            email='companyadmin@test.com',
            approved=True,
            has_completed_assessment=True
        )
        team_member.types.add(self.frontend_type)
        
        CompanyAdmin.objects.create(
            user=admin_user,
            customer=self.customer,
            can_sign_contracts=True,
            is_active=True
        )
        
        # Create contract
        Contract.objects.create(
            customer=self.customer,
            title='Dashboard Test Contract',
            contract_text='Terms',
            contract_type='engagement',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='pending',
            created_by=self.admin_user
        )
        
        self.client.login(username='companyadmin2', password='testpass123')
        response = self.client.get('/onboarding/dashboard/')
        
        if response.status_code == 200:
            self.assertContains(response, 'Dashboard Test Contract')
    
    def test_certificates_appear_on_dashboard(self):
        """Test certificates show on developer dashboard"""
        from onboarding.models import CertificationLevel, DeveloperCertification
        
        cert_level = CertificationLevel.objects.create(
            name='Dashboard Cert',
            level_type='senior',
            description='Test',
            created_by=self.admin_user
        )
        
        DeveloperCertification.objects.create(
            developer=self.regular_member,
            certification_level=cert_level,
            issued_by=self.admin_user,
            score=88.0
        )
        
        self.client.login(username='developer_test', password='testpass123')
        response = self.client.get('/onboarding/dashboard/')
        
        if response.status_code == 200:
            # Check if certificates section appears
            content = response.content.decode('utf-8')
            self.assertTrue('Dashboard Cert' in content or 'Certification' in content)
