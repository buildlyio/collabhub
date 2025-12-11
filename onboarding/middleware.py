"""
Middleware to enforce developer skill assessment completion.

This middleware checks if authenticated users have completed their mandatory
skill assessment and redirects them to the assessment landing page if not.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from onboarding.models import TeamMember


class AssessmentRequiredMiddleware(MiddlewareMixin):
    """
    Middleware to ensure all authenticated users complete their developer assessment.
    
    Redirects users to the assessment landing page if they haven't completed it,
    except for certain whitelisted URLs.
    """
    
    # URLs that don't require assessment completion
    EXEMPT_URLS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/register/',
        '/onboarding/register/',
        '/onboarding/dashboard/',  # Let dashboard view handle redirect
        '/onboarding/assessment/',
        '/onboarding/assessment/quiz/',
        '/onboarding/assessment/complete/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None
        
        # Skip if user is staff/superuser (admins)
        if request.user.is_staff or request.user.is_superuser:
            return None
        
        # Skip exempt URLs
        path = request.path
        for exempt_url in self.EXEMPT_URLS:
            if path.startswith(exempt_url):
                return None
        
        # Check if user has completed assessment
        try:
            team_member = TeamMember.objects.get(user=request.user)
            
            if not team_member.has_completed_assessment:
                # Redirect to assessment landing page
                assessment_url = reverse('onboarding:assessment_landing')
                if path != assessment_url:
                    return redirect(assessment_url)
        except TeamMember.DoesNotExist:
            # User doesn't have a team member profile yet
            pass
        
        return None
