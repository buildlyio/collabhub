"""
Context processor to add assessment completion status to all templates.

This makes assessment status available globally in templates so we can
show persistent reminders/notifications for incomplete assessments.
"""

from onboarding.models import TeamMember


def user_roles(request):
    """Provide role flags for templates: customer admin and staff.
    - is_company_admin: True if user has an active CompanyAdmin record
    - company_admin_customer: The customer associated with the admin (first active)
    - is_staff: Django staff user (super admin)
    - has_notifications: convenience flag for showing notifications link
    """
    from django.contrib.auth.models import AnonymousUser
    ctx = {
        "is_company_admin": False,
        "company_admin_customer": None,
        "is_staff": False,
        "has_notifications": False,
        "notification_count": 0,
    }

    user = getattr(request, "user", None)
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return ctx

    # Staff flag
    ctx["is_staff"] = bool(getattr(user, "is_staff", False))

    # CompanyAdmin detection
    try:
        from .models import CompanyAdmin
        admin_qs = CompanyAdmin.objects.filter(user=user, is_active=True)
        if admin_qs.exists():
            ctx["is_company_admin"] = True
            ctx["company_admin_customer"] = admin_qs.first().customer
    except Exception:
        # Avoid breaking templates if DB isn't ready
        pass

    # Notifications presence (lazy check)
    try:
        from .models import Notification
        unread_qs = Notification.objects.filter(recipient=user, is_read=False)
        ctx["has_notifications"] = unread_qs.exists()
        ctx["notification_count"] = unread_qs.count()
    except Exception:
        pass

    return ctx


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


def newsletter_reminder(request):
    """
    Add newsletter reminder for superadmins.
    
    Shows a reminder if:
    - User is a superuser
    - No newsletter has been sent this month
    - It's within the last 7 days of the month
    """
    context = {
        'show_newsletter_reminder': False,
    }
    
    # Only check for staff users
    if request.user.is_authenticated and request.user.is_staff:
        try:
            from onboarding.models import CommunityNewsletter
            context['show_newsletter_reminder'] = CommunityNewsletter.should_show_reminder()
        except Exception:
            pass
    
    return context
