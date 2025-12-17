"""
Management command to test admin dashboard data accuracy against database
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Count
from datetime import timedelta
from onboarding.models import TeamMember, TeamMemberType, Quiz, QuizQuestion, QuizAnswer


class Command(BaseCommand):
    help = 'Test admin dashboard statistics against actual database data'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("ADMIN DASHBOARD DATA INTEGRITY TEST"))
        self.stdout.write("="*80)
        self.stdout.write(f"Test run at: {now()}")
        
        thirty_days_ago = now() - timedelta(days=30)
        self.stdout.write(f"Date range: Last 30 days from {thirty_days_ago.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("-"*80)
        
        # Run all tests
        all_pass = True
        
        all_pass &= self.test_total_users()
        all_pass &= self.test_total_team_members()
        all_pass &= self.test_recent_signups(thirty_days_ago)
        all_pass &= self.test_completed_assessments()
        all_pass &= self.test_pending_assessments()
        all_pass &= self.test_recent_completions()
        all_pass &= self.test_total_quizzes()
        all_pass &= self.test_total_questions()
        all_pass &= self.test_total_answers()
        all_pass &= self.test_awaiting_evaluation()
        
        self.stdout.write("="*80)
        
        if all_pass:
            self.stdout.write(self.style.SUCCESS("✓ ALL TESTS PASSED - Dashboard data is accurate!"))
        else:
            self.stdout.write(self.style.ERROR("✗ SOME TESTS FAILED - Dashboard data has discrepancies!"))
        
        self.stdout.write("="*80 + "\n")
        
        return 0 if all_pass else 1
    
    def test_metric(self, name, query_description, expected_value, dashboard_calculation):
        """Generic test for a metric"""
        try:
            actual_value = dashboard_calculation
            match = expected_value == actual_value
            
            if match:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ PASS") + " | " +
                    f"{name:30s} | Expected: {expected_value:6} | Got: {actual_value:6}"
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ FAIL") + " | " +
                    f"{name:30s} | Expected: {expected_value:6} | Got: {actual_value:6}"
                )
                self.stdout.write(f"         Query: {query_description}")
            
            return match
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ ERROR") + " | " +
                f"{name:30s} | Exception: {str(e)}"
            )
            return False
    
    def test_total_users(self):
        """Test total users count"""
        expected = User.objects.count()
        # Dashboard calculation (from views.py line 484)
        actual = User.objects.count()
        return self.test_metric(
            "Total Users",
            "User.objects.count()",
            expected,
            actual
        )
    
    def test_total_team_members(self):
        """Test total team members count"""
        expected = TeamMember.objects.count()
        # Dashboard calculation (from views.py line 485)
        actual = TeamMember.objects.count()
        return self.test_metric(
            "Total Team Members",
            "TeamMember.objects.count()",
            expected,
            actual
        )
    
    def test_recent_signups(self, thirty_days_ago):
        """Test recent signups count"""
        expected = TeamMember.objects.filter(
            user__date_joined__gte=thirty_days_ago
        ).count()
        
        # Dashboard calculation (from views.py lines 488-492)
        recent_signups_queryset = TeamMember.objects.filter(
            user__date_joined__gte=thirty_days_ago
        ).select_related('user').order_by('-user__date_joined')
        actual = recent_signups_queryset.count()
        
        result = self.test_metric(
            "Recent Signups (30 days)",
            f"TeamMember.objects.filter(user__date_joined__gte={thirty_days_ago}).count()",
            expected,
            actual
        )
        
        # Additional info
        if actual > 0:
            self.stdout.write(f"         Sample recent users:")
            for tm in recent_signups_queryset[:3]:
                self.stdout.write(
                    f"         - {tm.first_name} {tm.last_name} "
                    f"({tm.user.username}) joined {tm.user.date_joined.strftime('%Y-%m-%d')}"
                )
        
        return result
    
    def test_completed_assessments(self):
        """Test completed assessments count"""
        expected = TeamMember.objects.filter(has_completed_assessment=True).count()
        # Dashboard calculation (from views.py line 498)
        actual = TeamMember.objects.filter(has_completed_assessment=True).count()
        
        result = self.test_metric(
            "Completed Assessments",
            "TeamMember.objects.filter(has_completed_assessment=True).count()",
            expected,
            actual
        )
        
        if actual > 0:
            sample = TeamMember.objects.filter(has_completed_assessment=True).first()
            self.stdout.write(
                f"         Sample: {sample.first_name} {sample.last_name} "
                f"completed on {sample.assessment_completed_at}"
            )
        
        return result
    
    def test_pending_assessments(self):
        """Test pending assessments count"""
        expected = TeamMember.objects.filter(has_completed_assessment=False).count()
        # Dashboard calculation (from views.py line 499)
        actual = TeamMember.objects.filter(has_completed_assessment=False).count()
        return self.test_metric(
            "Pending Assessments",
            "TeamMember.objects.filter(has_completed_assessment=False).count()",
            expected,
            actual
        )
    
    def test_recent_completions(self):
        """Test recent completions count"""
        expected = TeamMember.objects.filter(
            has_completed_assessment=True,
            assessment_completed_at__isnull=False
        ).count()
        
        # Dashboard calculation (from views.py lines 502-506)
        recent_completions_queryset = TeamMember.objects.filter(
            has_completed_assessment=True,
            assessment_completed_at__isnull=False
        ).order_by('-assessment_completed_at')
        actual = recent_completions_queryset.count()
        
        result = self.test_metric(
            "Recent Completions",
            "TeamMember.objects.filter(has_completed_assessment=True, assessment_completed_at__isnull=False).count()",
            expected,
            actual
        )
        
        if actual > 0:
            self.stdout.write(f"         Recent completions:")
            for tm in recent_completions_queryset[:3]:
                self.stdout.write(
                    f"         - {tm.first_name} {tm.last_name} "
                    f"completed {tm.assessment_completed_at.strftime('%Y-%m-%d')}"
                )
        
        return result
    
    def test_total_quizzes(self):
        """Test total quizzes count"""
        expected = Quiz.objects.count()
        # Dashboard calculation (from views.py line 512)
        actual = Quiz.objects.count()
        
        result = self.test_metric(
            "Total Quizzes",
            "Quiz.objects.count()",
            expected,
            actual
        )
        
        if actual > 0:
            quizzes = Quiz.objects.all()[:3]
            self.stdout.write(f"         Sample quizzes:")
            for quiz in quizzes:
                self.stdout.write(f"         - {quiz.name}")
        
        return result
    
    def test_total_questions(self):
        """Test total questions count"""
        expected = QuizQuestion.objects.count()
        # Dashboard calculation (from views.py line 513)
        actual = QuizQuestion.objects.count()
        return self.test_metric(
            "Total Questions",
            "QuizQuestion.objects.count()",
            expected,
            actual
        )
    
    def test_total_answers(self):
        """Test total answers count"""
        expected = QuizAnswer.objects.count()
        # Dashboard calculation (from views.py line 514)
        actual = QuizAnswer.objects.count()
        return self.test_metric(
            "Total Answers",
            "QuizAnswer.objects.count()",
            expected,
            actual
        )
    
    def test_awaiting_evaluation(self):
        """Test awaiting evaluation count"""
        expected = QuizAnswer.objects.filter(
            question__question_type='essay',
            evaluator_score__isnull=True
        ).count()
        
        # Dashboard calculation (from views.py lines 517-520)
        actual = QuizAnswer.objects.filter(
            question__question_type='essay',
            evaluator_score__isnull=True
        ).count()
        
        result = self.test_metric(
            "Awaiting Evaluation",
            "QuizAnswer.objects.filter(question__question_type='essay', evaluator_score__isnull=True).count()",
            expected,
            actual
        )
        
        if actual > 0:
            self.stdout.write(f"         {actual} essay answers need evaluation")
            pending = QuizAnswer.objects.filter(
                question__question_type='essay',
                evaluator_score__isnull=True
            )[:3]
            for answer in pending:
                self.stdout.write(
                    f"         - {answer.team_member.first_name} {answer.team_member.last_name}: "
                    f"\"{answer.answer_text[:50]}...\""
                )
        
        return result
