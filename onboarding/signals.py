"""
Email notification signals for CollabHub
Sends admin notifications when new users register
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import TeamMember
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=TeamMember)
def notify_admin_new_team_member(sender, instance, created, **kwargs):
    """
    Send email notification to admin when a new team member registers
    """
    if created:
        try:
            # Email details
            subject = f'New Team Member Registration: {instance.first_name} {instance.last_name}'
            
            message = f"""
A new team member has registered on CollabHub:

Name: {instance.first_name} {instance.last_name}
Email: {instance.email}
Type: {', '.join([t.name for t in instance.types.all()]) if hasattr(instance, 'types') else 'Team Member'}
LinkedIn: {instance.linkedin or 'Not provided'}
GitHub: {instance.github_account or 'Not provided'}
Experience: {instance.experience_years} years
Bio: {instance.bio[:200] if instance.bio else 'Not provided'}

Profile Types: {', '.join([t.name for t in instance.types.all()]) if instance.types.exists() else 'None'}

Agency: {instance.agency.name if instance.agency else ('Independent' if instance.is_independent else instance.agency_name_text)}

Status: Awaiting approval and assessment completion

Review Profile: https://collab.buildly.io/onboarding/admin-developer-profile/{instance.id}/
Admin Dashboard: https://collab.buildly.io/onboarding/admin-dashboard/
            """
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.DEFAULT_FROM_EMAIL, 'admin@buildly.io']
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=True,  # Don't break registration if email fails
            )
            
            logger.info(f"Admin notification sent for new team member: {instance.email}")
            
        except Exception as e:
            logger.error(f"Failed to send admin notification for {instance.email}: {str(e)}")
            # Don't raise exception - email failure shouldn't break registration


@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    """
    Send email notification to admin when a new user registers (non-team member)
    This catches regular Django user registrations that aren't team members
    """
    if created:
        # Check if this user has a team member profile
        # If they do, the team member signal will handle it
        if hasattr(instance, 'team_member'):
            return
            
        try:
            subject = f'New User Registration: {instance.username}'
            
            message = f"""
A new user has registered on CollabHub:

Username: {instance.username}
Email: {instance.email}
Name: {instance.get_full_name() or 'Not provided'}
Date Joined: {instance.date_joined.strftime('%Y-%m-%d %H:%M:%S')}

Admin Dashboard: https://collab.buildly.io/admin/auth/user/{instance.id}/change/
            """
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.DEFAULT_FROM_EMAIL, 'admin@buildly.io']
            
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=True,
            )
            
            logger.info(f"Admin notification sent for new user: {instance.username}")
            
        except Exception as e:
            logger.error(f"Failed to send admin notification for {instance.username}: {str(e)}")
