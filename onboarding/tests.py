"""
Tests for the onboarding app, specifically admin dashboard data accuracy
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from onboarding.models import TeamMember, TeamMemberType, Quiz, QuizQuestion, QuizAnswer
from onboarding.views import admin_dashboard


class AdminDashboardDataTest(TestCase):
    """Test that admin dashboard displays accurate data from the database"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data that won't be modified by tests"""
        # Create admin user
        cls.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        
        # Create some regular users with different signup dates
        thirty_days_ago = now() - timedelta(days=30)
        forty_days_ago = now() - timedelta(days=40)
        
        # Recent signups (within 30 days)
        cls.recent_user1 = User.objects.create_user(
            username='recent1',
            email='recent1@test.com',
            password='pass123',
            date_joined=now() - timedelta(days=10)
        )
        cls.recent_user2 = User.objects.create_user(
            username='recent2',
            email='recent2@test.com',
            password='pass123',
            date_joined=now() - timedelta(days=20)
        )
        
        # Old signup (over 30 days ago)
        cls.old_user = User.objects.create_user(
            username='old1',
            email='old1@test.com',
            password='pass123',
            date_joined=forty_days_ago
        )
        
        # Create team members
        cls.tm_recent1 = TeamMember.objects.create(
            user=cls.recent_user1,
            team_member_type='buildly-hire-frontend',
            first_name='Recent',
            last_name='User1',
            email='recent1@test.com',
            has_completed_assessment=False
        )
        
        cls.tm_recent2 = TeamMember.objects.create(
            user=cls.recent_user2,
            team_member_type='buildly-hire-backend',
            first_name='Recent',
            last_name='User2',
            email='recent2@test.com',
            has_completed_assessment=True,
            assessment_completed_at=now() - timedelta(days=15)
        )
        
        cls.tm_old = TeamMember.objects.create(
            user=cls.old_user,
            team_member_type='buildly-hire-ai',
            first_name='Old',
            last_name='User',
            email='old1@test.com',
            has_completed_assessment=True,
            assessment_completed_at=forty_days_ago + timedelta(days=5)
        )
        
        # Create a quiz
        cls.quiz = Quiz.objects.create(
            name='Test Assessment Quiz',
            url='https://example.com/quiz',
            available_date=now() - timedelta(days=60)
        )
        
        # Create questions
        cls.mc_question = QuizQuestion.objects.create(
            quiz=cls.quiz,
            question_text='What is 2+2?',
            question_type='multiple_choice'
        )
        
        cls.essay_question = QuizQuestion.objects.create(
            quiz=cls.quiz,
            question_text='Explain your experience.',
            question_type='essay'
        )
        
        # Create answers
        cls.mc_answer = QuizAnswer.objects.create(
            team_member=cls.tm_recent2,
            question=cls.mc_question,
            answer_text='4'
        )
        
        # Essay answer without evaluation
        cls.essay_answer_pending = QuizAnswer.objects.create(
            team_member=cls.tm_recent2,
            question=cls.essay_question,
            answer_text='I have 5 years of experience...',
            evaluator_score=None  # Not evaluated yet
        )
        
        # Essay answer with evaluation
        cls.essay_answer_evaluated = QuizAnswer.objects.create(
            team_member=cls.tm_old,
            question=cls.essay_question,
            answer_text='I have 10 years of experience...',
            evaluator_score=8
        )
    
    def setUp(self):
        """Set up for each test"""
        self.client = Client()
        self.client.force_login(self.admin_user)
    
    def test_total_users_count(self):
        """Test that total users count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = User.objects.count()
        actual_count = response.context['total_users']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Total users mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_total_team_members_count(self):
        """Test that total team members count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = TeamMember.objects.count()
        actual_count = response.context['total_team_members']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Total team members mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_recent_signups_count(self):
        """Test that recent signups count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        thirty_days_ago = now() - timedelta(days=30)
        expected_count = TeamMember.objects.filter(
            user__date_joined__gte=thirty_days_ago
        ).count()
        
        actual_count = response.context['recent_signups_count']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Recent signups mismatch: Dashboard shows {actual_count}, DB has {expected_count} "
            f"(checking users joined since {thirty_days_ago})"
        )
    
    def test_completed_assessments_count(self):
        """Test that completed assessments count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = TeamMember.objects.filter(has_completed_assessment=True).count()
        actual_count = response.context['completed_assessments']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Completed assessments mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_pending_assessments_count(self):
        """Test that pending assessments count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = TeamMember.objects.filter(has_completed_assessment=False).count()
        actual_count = response.context['pending_assessments']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Pending assessments mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_recent_completions_count(self):
        """Test that recent completions count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = TeamMember.objects.filter(
            has_completed_assessment=True,
            assessment_completed_at__isnull=False
        ).count()
        
        actual_count = response.context['recent_completions_count']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Recent completions mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_total_quizzes_count(self):
        """Test that total quizzes count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = Quiz.objects.count()
        actual_count = response.context['total_quizzes']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Total quizzes mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_total_questions_count(self):
        """Test that total questions count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = QuizQuestion.objects.count()
        actual_count = response.context['total_questions']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Total questions mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_total_answers_count(self):
        """Test that total answers count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = QuizAnswer.objects.count()
        actual_count = response.context['total_answers']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Total answers mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_awaiting_evaluation_count(self):
        """Test that awaiting evaluation count is accurate"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        # Direct database query
        expected_count = QuizAnswer.objects.filter(
            question__question_type='essay',
            evaluator_score__isnull=True
        ).count()
        
        actual_count = response.context['awaiting_evaluation']
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Awaiting evaluation mismatch: Dashboard shows {actual_count}, DB has {expected_count}"
        )
    
    def test_recent_signups_list_accuracy(self):
        """Test that recent signups list contains correct items"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        recent_signups = response.context['recent_signups']
        recent_ids = [tm.id for tm in recent_signups]
        
        # Should include recent users
        self.assertIn(self.tm_recent1.id, recent_ids, "Recent user 1 should be in recent signups")
        self.assertIn(self.tm_recent2.id, recent_ids, "Recent user 2 should be in recent signups")
        
        # Should NOT include old users
        self.assertNotIn(self.tm_old.id, recent_ids, "Old user should NOT be in recent signups")
    
    def test_recent_completions_list_accuracy(self):
        """Test that recent completions list contains correct items"""
        response = self.client.get('/onboarding/admin-dashboard/')
        
        recent_completions = response.context['recent_completions']
        completion_ids = [tm.id for tm in recent_completions]
        
        # Should include only users with completed assessments
        self.assertNotIn(self.tm_recent1.id, completion_ids, "User without completed assessment should NOT be in completions")
        self.assertIn(self.tm_recent2.id, completion_ids, "User with completed assessment should be in completions")
        self.assertIn(self.tm_old.id, completion_ids, "Old user with completed assessment should be in completions")


class AdminDashboardProductionDataTest(TestCase):
    """
    Run this test against production database to verify data accuracy.
    This test doesn't create data, it just queries existing production data.
    """
    
    def test_production_data_integrity(self):
        """
        Compare dashboard queries with direct database queries on production data.
        Run with: python manage.py test onboarding.tests.AdminDashboardProductionDataTest
        """
        from django.db.models import Count
        from onboarding.models import TeamMemberType
        
        thirty_days_ago = now() - timedelta(days=30)
        
        # Get expected values directly from database
        expected = {
            'total_users': User.objects.count(),
            'total_team_members': TeamMember.objects.count(),
            'recent_signups_count': TeamMember.objects.filter(
                user__date_joined__gte=thirty_days_ago
            ).count(),
            'completed_assessments': TeamMember.objects.filter(has_completed_assessment=True).count(),
            'pending_assessments': TeamMember.objects.filter(has_completed_assessment=False).count(),
            'recent_completions_count': TeamMember.objects.filter(
                has_completed_assessment=True,
                assessment_completed_at__isnull=False
            ).count(),
            'total_quizzes': Quiz.objects.count(),
            'total_questions': QuizQuestion.objects.count(),
            'total_answers': QuizAnswer.objects.count(),
            'awaiting_evaluation': QuizAnswer.objects.filter(
                question__question_type='essay',
                evaluator_score__isnull=True
            ).count(),
        }
        
        # Get actual values from dashboard view
        client = Client()
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            self.skipTest("No admin user found in database")
        
        client.force_login(admin_user)
        response = client.get('/onboarding/admin-dashboard/')
        
        # Compare each metric
        errors = []
        for key, expected_value in expected.items():
            actual_value = response.context.get(key)
            if actual_value != expected_value:
                errors.append(
                    f"{key}: Dashboard={actual_value}, Database={expected_value}"
                )
        
        # Print detailed report
        print("\n" + "="*80)
        print("ADMIN DASHBOARD DATA INTEGRITY REPORT")
        print("="*80)
        print(f"Checked at: {now()}")
        print(f"Date range: Last 30 days from {thirty_days_ago}")
        print("-"*80)
        
        for key, expected_value in expected.items():
            actual_value = response.context.get(key)
            status = "✓ PASS" if actual_value == expected_value else "✗ FAIL"
            print(f"{status} | {key:30s} | Dashboard: {actual_value:6} | Database: {expected_value:6}")
        
        print("="*80)
        
        if errors:
            self.fail(f"Data mismatches found:\n" + "\n".join(errors))
        else:
            print("✓ All dashboard data matches database!")
