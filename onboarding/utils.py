# onboarding/utils.py - Utilities for Phase 1 Portal

import os
import base64
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime


# Default site URL fallback
DEFAULT_SITE_URL = 'https://collab.buildly.io'

def get_site_url():
    """Safely get SITE_URL from settings with fallback"""
    return getattr(settings, 'SITE_URL', None) or DEFAULT_SITE_URL


# ===== ENCRYPTION UTILITIES =====

def get_encryption_key():
    """Get or create encryption key for tokens"""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        # Generate and save to .env if not exists
        key = Fernet.generate_key().decode()
    return key.encode() if isinstance(key, str) else key


def encrypt_token(token: str) -> str:
    """Encrypt a token (GitHub token, Labs token, etc)"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(token.encode())
        return encrypted.decode()
    except Exception as e:
        # Fallback: just base64 encode if encryption fails
        return base64.b64encode(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted token"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception as e:
        # Fallback: try base64 decode
        try:
            return base64.b64decode(encrypted_token.encode()).decode()
        except:
            return None


# ===== EMAIL UTILITIES =====

def send_email(to_email: str, subject: str, template_name: str, context: dict, from_email: str = None, bcc: list = None):
    """
    Send email using MailerSend
    
    Args:
        to_email: Recipient email
        subject: Email subject
        template_name: Template file path (e.g., 'emails/community_approval.html')
        context: Context data for template
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
        bcc: List of BCC email addresses
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL or 'noreply@buildly.io'
    
    try:
        # Render HTML and text versions
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email],
            bcc=bcc or []
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send via MailerSend
        result = email.send()
        logger.info(f"Email sent successfully to {to_email}: subject='{subject}', result={result}")
        print(f"[EMAIL] Sent to {to_email}: {subject} (result: {result})")
        return result
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {str(e)}")
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {str(e)}")
        return False


def send_community_approval_email(team_member, profile_type=None):
    """Email sent when developer approved to Buildly community"""
    site_url = get_site_url()
    
    # Get the profile type label if available
    profile_type_label = None
    if profile_type:
        profile_type_label = profile_type.label if hasattr(profile_type, 'label') else str(profile_type)
    elif team_member.profile_types.exists():
        profile_type_label = team_member.profile_types.first().label
    
    context = {
        'first_name': team_member.first_name,
        'developer_name': f"{team_member.first_name} {team_member.last_name}",
        'profile_type': profile_type_label,
        'buildly_url': site_url,
        'login_url': f"{site_url}/login",
        'resources_url': f"{site_url}/onboarding/resources",
        'certifications_url': f"{site_url}/onboarding/certificates/",
    }
    
    return send_email(
        to_email=team_member.email,
        subject="Welcome to Buildly Open Source Community!",
        template_name='emails/community_approval.html',
        context=context
    )


def send_community_revocation_email(team_member):
    """Email sent when developer's community access is revoked"""
    site_url = get_site_url()
    context = {
        'first_name': team_member.first_name,
        'developer_name': f"{team_member.first_name} {team_member.last_name}",
        'buildly_url': site_url,
    }
    
    return send_email(
        to_email=team_member.email,
        subject="Buildly Community Access Update",
        template_name='emails/community_revocation.html',
        context=context
    )


def send_assessment_reminder_email(team_member, reminder_count):
    """Email sent to remind developer to complete their assessment"""
    site_url = get_site_url()
    
    # Customize subject based on reminder count
    if reminder_count == 1:
        subject = "Reminder: Complete Your Buildly Developer Assessment"
    elif reminder_count == 2:
        subject = "Second Reminder: Your Buildly Assessment Awaits"
    else:
        subject = "Final Reminder: Complete Your Assessment to Join Buildly Community"
    
    context = {
        'first_name': team_member.first_name,
        'developer_name': f"{team_member.first_name} {team_member.last_name}",
        'reminder_count': reminder_count,
        'is_final_reminder': reminder_count >= 3,
        'buildly_url': site_url,
        'login_url': f"{site_url}/login",
        'assessment_url': f"{site_url}/onboarding/assessment",
    }
    
    return send_email(
        to_email=team_member.email,
        subject=subject,
        template_name='emails/assessment_reminder.html',
        context=context,
        bcc=['admin@buildly.io']
    )


def send_team_approval_email(customer_developer_assignment):
    """Email sent when developer approved to customer team"""
    developer = customer_developer_assignment.developer
    customer = customer_developer_assignment.customer
    
    context = {
        'first_name': developer.first_name,
        'customer_name': customer.company_name,
        'buildly_url': get_site_url(),
    }
    
    return send_email(
        to_email=developer.email,
        subject=f"You've been approved to {customer.company_name}!",
        template_name='emails/team_approval.html',
        context=context
    )


def send_contract_ready_email(contract, user):
    """Email sent when contract is ready to sign"""
    site_url = get_site_url()
    context = {
        'first_name': user.first_name,
        'contract_title': contract.title,
        'customer_name': contract.customer.company_name,
        'sign_url': f"{site_url}/customer/contracts/{contract.id}/sign/",
        'buildly_url': site_url,
    }
    
    return send_email(
        to_email=user.email,
        subject=f"Contract Ready to Sign: {contract.title}",
        template_name='emails/contract_ready_sign.html',
        context=context
    )


def send_contract_signed_email(contract, user):
    """Email confirmation sent when contract signed"""
    site_url = get_site_url()
    context = {
        'first_name': user.first_name,
        'contract_title': contract.title,
        'customer_name': contract.customer.company_name,
        'signed_at': contract.signed_at.strftime('%B %d, %Y'),
        'pdf_url': f"{site_url}/customer/contracts/{contract.id}/pdf/",
        'buildly_url': site_url,
    }
    
    return send_email(
        to_email=user.email,
        subject=f"Contract Signed Confirmation",
        template_name='emails/contract_signed_confirmation.html',
        context=context
    )


def send_removal_request_email(admin_user, developer, customer):
    """Email sent when removal request is made"""
    context = {
        'first_name': admin_user.first_name,
        'developer_name': f"{developer.first_name} {developer.last_name}",
        'customer_name': customer.company_name,
        'days_notice': 30,
        'admin_url': f"{get_site_url()}/admin/approvals/",
    }
    
    return send_email(
        to_email=admin_user.email,
        subject=f"Developer Removal Request: {developer.first_name} {developer.last_name}",
        template_name='emails/team_removal_requested.html',
        context=context
    )


# ===== PDF UTILITIES =====

def generate_contract_pdf(contract, signature_data=None, signed_by=None, signed_at=None, ip_address=None):
    """
    Generate PDF for contract with optional signature details
    
    Args:
        contract: Contract instance
        signature_data: Base64 encoded signature image
        signed_by: Name of signer
        signed_at: Signature timestamp
        ip_address: IP address of signer
    
    Returns:
        PDF as BytesIO object
    """
    try:
        # Create PDF buffer
        pdf_buffer = io.BytesIO()
        doc = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter
        
        # Header
        doc.setFont("Helvetica-Bold", 16)
        doc.drawString(50, height - 50, contract.title)
        
        doc.setFont("Helvetica", 10)
        doc.drawString(50, height - 70, f"Customer: {contract.customer.company_name}")
        doc.drawString(50, height - 85, f"Period: {contract.start_date} to {contract.end_date}")
        
        # Contract text
        doc.setFont("Helvetica", 10)
        y_position = height - 120
        
        # Wrap contract text
        text_lines = contract.contract_text.split('\n')
        for line in text_lines[:30]:  # Limit to first 30 lines
            if y_position < 100:
                doc.showPage()
                y_position = height - 50
            doc.drawString(50, y_position, line[:100])  # Limit line length
            y_position -= 15
        
        # Signature section if signed
        if signed_by and signed_at:
            y_position -= 30
            doc.setFont("Helvetica-Bold", 12)
            doc.drawString(50, y_position, "Signed:")
            y_position -= 20
            
            doc.setFont("Helvetica", 10)
            doc.drawString(50, y_position, f"Signed by: {signed_by}")
            y_position -= 15
            doc.drawString(50, y_position, f"Date: {signed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            y_position -= 15
            if ip_address:
                doc.drawString(50, y_position, f"IP Address: {ip_address}")
            
            # Draw signature image if provided
            if signature_data:
                try:
                    # Decode base64 signature
                    sig_image = io.BytesIO(base64.b64decode(signature_data))
                    doc.drawImage(sig_image, 50, y_position - 80, width=200, height=60)
                except:
                    pass  # If signature image fails, just skip it
        
        doc.save()
        pdf_buffer.seek(0)
        return pdf_buffer
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None


# ===== TOKEN UTILITIES =====

def generate_secure_token(length=32):
    """Generate a secure random token"""
    import secrets
    return secrets.token_urlsafe(length)


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ===== MAILERSEND API ANALYTICS =====

def get_mailersend_api_key():
    """Get MailerSend API key from environment"""
    return os.environ.get('MAILERSEND_API_KEY')


def fetch_mailersend_analytics(date_from=None, date_to=None):
    """
    Fetch email analytics from MailerSend API
    
    Returns aggregated stats for: delivered, opened, clicked, bounced, spam_complaints
    """
    import requests
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    api_key = get_mailersend_api_key()
    
    if not api_key:
        logger.warning("MAILERSEND_API_KEY not configured")
        return None
    
    # Default to last 30 days if no dates provided
    if not date_to:
        date_to = datetime.now()
    if not date_from:
        date_from = date_to - timedelta(days=30)
    
    # Format dates for API (UNIX timestamp in milliseconds)
    date_from_ts = int(date_from.timestamp() * 1000)
    date_to_ts = int(date_to.timestamp() * 1000)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Fetch activity analytics
        url = 'https://api.mailersend.com/v1/analytics/date'
        params = {
            'date_from': date_from_ts,
            'date_to': date_to_ts,
            'event': ['delivered', 'opened', 'clicked', 'soft_bounced', 'hard_bounced', 'spam_complaints', 'unsubscribed'],
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"MailerSend API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching MailerSend analytics: {str(e)}")
        return None


def fetch_mailersend_activity(page=1, limit=25, event_type=None, date_from=None, date_to=None):
    """
    Fetch detailed email activity from MailerSend API
    
    Args:
        page: Page number for pagination
        limit: Number of results per page
        event_type: Filter by event type (e.g., 'opened', 'clicked', 'bounced')
        date_from: Start date for filtering
        date_to: End date for filtering
    
    Returns activity list with recipient details
    """
    import requests
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    api_key = get_mailersend_api_key()
    
    if not api_key:
        logger.warning("MAILERSEND_API_KEY not configured")
        return None
    
    # Default to last 30 days if no dates provided
    if not date_to:
        date_to = datetime.now()
    if not date_from:
        date_from = date_to - timedelta(days=30)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    try:
        url = 'https://api.mailersend.com/v1/activity'
        params = {
            'page': page,
            'limit': limit,
            'date_from': int(date_from.timestamp()),
            'date_to': int(date_to.timestamp()),
        }
        
        if event_type:
            params['event'] = event_type
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"MailerSend activity API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching MailerSend activity: {str(e)}")
        return None


def fetch_mailersend_messages(page=1, limit=25):
    """
    Fetch sent messages from MailerSend API
    
    Returns list of messages with delivery status
    """
    import requests
    import logging
    
    logger = logging.getLogger(__name__)
    api_key = get_mailersend_api_key()
    
    if not api_key:
        logger.warning("MAILERSEND_API_KEY not configured")
        return None
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    try:
        url = 'https://api.mailersend.com/v1/messages'
        params = {
            'page': page,
            'limit': limit,
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"MailerSend messages API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching MailerSend messages: {str(e)}")
        return None


def get_email_analytics_summary():
    """
    Get a summary of email analytics for the dashboard
    
    Returns dict with:
    - total_sent, total_delivered, total_opened, total_clicked
    - bounce_rate, open_rate, click_rate
    - recent_bounces, recent_spam_complaints
    """
    import logging
    from datetime import datetime, timedelta
    
    logger = logging.getLogger(__name__)
    
    # Fetch analytics for last 30 days
    analytics = fetch_mailersend_analytics()
    
    if not analytics:
        return {
            'api_configured': bool(get_mailersend_api_key()),
            'error': 'Unable to fetch analytics from MailerSend',
        }
    
    # Parse the analytics data
    data = analytics.get('data', {})
    stats = data.get('stats', [])
    
    # Aggregate totals
    totals = {
        'delivered': 0,
        'opened': 0,
        'clicked': 0,
        'soft_bounced': 0,
        'hard_bounced': 0,
        'spam_complaints': 0,
        'unsubscribed': 0,
    }
    
    for stat in stats:
        event = stat.get('event')
        count = stat.get('count', 0)
        if event in totals:
            totals[event] = count
    
    total_sent = totals['delivered'] + totals['soft_bounced'] + totals['hard_bounced']
    total_bounces = totals['soft_bounced'] + totals['hard_bounced']
    
    # Calculate rates (avoid division by zero)
    open_rate = (totals['opened'] / totals['delivered'] * 100) if totals['delivered'] > 0 else 0
    click_rate = (totals['clicked'] / totals['opened'] * 100) if totals['opened'] > 0 else 0
    bounce_rate = (total_bounces / total_sent * 100) if total_sent > 0 else 0
    
    return {
        'api_configured': True,
        'total_sent': total_sent,
        'total_delivered': totals['delivered'],
        'total_opened': totals['opened'],
        'total_clicked': totals['clicked'],
        'total_bounces': total_bounces,
        'soft_bounces': totals['soft_bounced'],
        'hard_bounces': totals['hard_bounced'],
        'spam_complaints': totals['spam_complaints'],
        'unsubscribes': totals['unsubscribed'],
        'open_rate': round(open_rate, 1),
        'click_rate': round(click_rate, 1),
        'bounce_rate': round(bounce_rate, 1),
        'period_days': 30,
    }
