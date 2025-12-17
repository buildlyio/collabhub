"""
Simple script to query database and print dashboard statistics
Run with: python3 check_dashboard_stats.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.production')
django.setup()

from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from onboarding.models import TeamMember, Quiz, QuizQuestion, QuizAnswer

print("\n" + "="*80)
print("DATABASE QUERY RESULTS FOR DASHBOARD")
print("="*80)

thirty_days_ago = now() - timedelta(days=30)
print(f"Current time: {now()}")
print(f"30 days ago: {thirty_days_ago}")
print("-"*80)

# Query all metrics
print("\nUSER STATISTICS:")
total_users = User.objects.count()
print(f"  Total Django Users: {total_users}")

total_team_members = TeamMember.objects.count()
print(f"  Total Team Members: {total_team_members}")

recent_signups = TeamMember.objects.filter(
    user__date_joined__gte=thirty_days_ago
).count()
print(f"  Recent Signups (30 days): {recent_signups}")

# Show sample recent signups
if recent_signups > 0:
    print(f"\n  Sample recent signups:")
    for tm in TeamMember.objects.filter(user__date_joined__gte=thirty_days_ago).select_related('user')[:5]:
        print(f"    - {tm.first_name} {tm.last_name} joined {tm.user.date_joined.strftime('%Y-%m-%d')}")

print("\nASSESSMENT STATISTICS:")
completed = TeamMember.objects.filter(has_completed_assessment=True).count()
print(f"  Completed Assessments: {completed}")

pending = TeamMember.objects.filter(has_completed_assessment=False).count()
print(f"  Pending Assessments: {pending}")

recent_completions = TeamMember.objects.filter(
    has_completed_assessment=True,
    assessment_completed_at__isnull=False
).count()
print(f"  Recent Completions: {recent_completions}")

# Show sample completions
if recent_completions > 0:
    print(f"\n  Sample completions:")
    for tm in TeamMember.objects.filter(
        has_completed_assessment=True,
        assessment_completed_at__isnull=False
    ).order_by('-assessment_completed_at')[:5]:
        print(f"    - {tm.first_name} {tm.last_name} completed {tm.assessment_completed_at.strftime('%Y-%m-%d')}")

print("\nQUIZ STATISTICS:")
total_quizzes = Quiz.objects.count()
print(f"  Total Quizzes: {total_quizzes}")

total_questions = QuizQuestion.objects.count()
print(f"  Total Questions: {total_questions}")

total_answers = QuizAnswer.objects.count()
print(f"  Total Answers: {total_answers}")

awaiting_eval = QuizAnswer.objects.filter(
    question__question_type='essay',
    evaluator_score__isnull=True
).count()
print(f"  Awaiting Evaluation: {awaiting_eval}")

# Show sample quizzes
if total_quizzes > 0:
    print(f"\n  Sample quizzes:")
    for quiz in Quiz.objects.all()[:3]:
        q_count = quiz.questions.count()
        print(f"    - {quiz.name} ({q_count} questions)")

print("\n" + "="*80)
print("EXPECTED DASHBOARD VALUES:")
print("="*80)
print(f"Total Users: {total_users}")
print(f"Total Team Members: {total_team_members}")
print(f"New (30 days): {recent_signups}")
print(f"Completed Assessments: {completed}")
print(f"Pending Assessments: {pending}")
print(f"Recent Completions: {recent_completions}")
print(f"Total Quizzes: {total_quizzes}")
print(f"Total Questions: {total_questions}")
print(f"Total Answers: {total_answers}")
print(f"Awaiting Evaluation: {awaiting_eval}")
print("="*80 + "\n")
