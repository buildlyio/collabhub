"""
Context processor to add assessment completion status to all templates.

This makes assessment status available globally in templates so we can
show persistent reminders/notifications for incomplete assessments.
"""

from onboarding.models import TeamMember


def assessment_status(request):
    """
    Add assessment completion status to template context.
    
    Returns a dictionary with:
    - needs_assessment: Boolean indicating if user needs to complete assessment
    - assessment_reminder_count: Number of times user has been reminded
    """
    context = {
        'needs_assessment': False,
        'assessment_reminder_count': 0,
    }
    
    # Only check for authenticated users
    if request.user.is_authenticated:
        try:
            team_member = TeamMember.objects.get(user=request.user)
            context['needs_assessment'] = not team_member.has_completed_assessment
            context['assessment_reminder_count'] = team_member.assessment_reminder_count
        except TeamMember.DoesNotExist:
            pass
    
    return context
