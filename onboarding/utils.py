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

def send_email(to_email: str, subject: str, template_name: str, context: dict, from_email: str = None):
    """
    Send email using MailerSend
    
    Args:
        to_email: Recipient email
        subject: Email subject
        template_name: Template file path (e.g., 'emails/community_approval.html')
        context: Context data for template
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
    """
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
            to=[to_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send via MailerSend
        return email.send()
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False


def send_community_approval_email(team_member):
    """Email sent when developer approved to Buildly community"""
    context = {
        'first_name': team_member.first_name,
        'developer_name': f"{team_member.first_name} {team_member.last_name}",
        'buildly_url': settings.SITE_URL or 'https://collab.buildly.io',
        'login_url': f"{settings.SITE_URL or 'https://collab.buildly.io'}/login",
        'resources_url': f"{settings.SITE_URL or 'https://collab.buildly.io'}/onboarding/resources",
        'certifications_url': f"{settings.SITE_URL or 'https://collab.buildly.io'}/onboarding/certificates/",
    }
    
    return send_email(
        to_email=team_member.email,
        subject="Welcome to Buildly Open Source Community!",
        template_name='emails/community_approval.html',
        context=context
    )


def send_team_approval_email(customer_developer_assignment):
    """Email sent when developer approved to customer team"""
    developer = customer_developer_assignment.developer
    customer = customer_developer_assignment.customer
    
    context = {
        'first_name': developer.first_name,
        'customer_name': customer.company_name,
        'buildly_url': settings.SITE_URL or 'https://collab.buildly.io',
    }
    
    return send_email(
        to_email=developer.email,
        subject=f"You've been approved to {customer.company_name}!",
        template_name='emails/team_approval.html',
        context=context
    )


def send_contract_ready_email(contract, user):
    """Email sent when contract is ready to sign"""
    context = {
        'first_name': user.first_name,
        'contract_title': contract.title,
        'customer_name': contract.customer.company_name,
        'sign_url': f"{settings.SITE_URL}/customer/contracts/{contract.id}/sign/",
        'buildly_url': settings.SITE_URL or 'https://collab.buildly.io',
    }
    
    return send_email(
        to_email=user.email,
        subject=f"Contract Ready to Sign: {contract.title}",
        template_name='emails/contract_ready_sign.html',
        context=context
    )


def send_contract_signed_email(contract, user):
    """Email confirmation sent when contract signed"""
    context = {
        'first_name': user.first_name,
        'contract_title': contract.title,
        'customer_name': contract.customer.company_name,
        'signed_at': contract.signed_at.strftime('%B %d, %Y'),
        'pdf_url': f"{settings.SITE_URL}/customer/contracts/{contract.id}/pdf/",
        'buildly_url': settings.SITE_URL or 'https://collab.buildly.io',
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
        'admin_url': f"{settings.SITE_URL}/admin/approvals/",
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
