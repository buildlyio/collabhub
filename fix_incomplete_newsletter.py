#!/usr/bin/env python
"""
Script to fix the incomplete newsletter that stopped at 10/18 recipients.
Creates pending NewsletterRecipient records for developers who didn't receive it.

Run with: python manage.py shell < fix_incomplete_newsletter.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from onboarding.models import CommunityNewsletter, NewsletterRecipient, DeveloperProfile

# Get the most recent newsletter
newsletter = CommunityNewsletter.objects.order_by('-sent_at').first()

if not newsletter:
    print("No newsletters found!")
    exit()

print(f"\n📧 Found newsletter: '{newsletter.subject}'")
print(f"   Sent: {newsletter.sent_at}")
print(f"   Current recipient_count: {newsletter.recipient_count}")
print(f"   Current failed_count: {newsletter.failed_count}")

# Check existing recipients
existing_recipients = newsletter.recipients.all()
existing_count = existing_recipients.count()
print(f"\n   Existing recipient records: {existing_count}")

if existing_count > 0:
    sent = existing_recipients.filter(status='sent').count()
    failed = existing_recipients.filter(status='failed').count()
    pending = existing_recipients.filter(status='pending').count()
    print(f"   - Sent: {sent}, Failed: {failed}, Pending: {pending}")
    
    if pending > 0:
        print(f"\n✅ This newsletter already has {pending} pending recipients.")
        print("   Go to the newsletter detail page and click 'Start/Resume Sending' to continue.")
        exit()

# Get all approved developers who should receive newsletters
all_developers = DeveloperProfile.objects.filter(
    user__is_active=True,
    approval_status='approved'
).exclude(user__email='')

print(f"\n👥 Total approved developers: {all_developers.count()}")

# Get emails already sent (from existing recipient records)
already_sent_emails = set(
    existing_recipients.filter(status='sent').values_list('email', flat=True)
)
print(f"   Already sent to: {len(already_sent_emails)} developers")

# Find developers who didn't get the email
developers_to_add = []
for dev in all_developers:
    if dev.user.email and dev.user.email not in already_sent_emails:
        developers_to_add.append(dev)

print(f"   Need to send to: {len(developers_to_add)} developers")

if not developers_to_add:
    print("\n✅ All developers have already received this newsletter!")
    exit()

# Ask for confirmation
print(f"\n⚠️  This will create {len(developers_to_add)} pending recipient records.")
print("   After running, go to the newsletter detail page and click 'Start/Resume Sending'.")
confirm = input("\nProceed? (yes/no): ")

if confirm.lower() != 'yes':
    print("Cancelled.")
    exit()

# Create pending recipient records
created = 0
for dev in developers_to_add:
    NewsletterRecipient.objects.get_or_create(
        newsletter=newsletter,
        email=dev.user.email,
        defaults={
            'developer': dev,
            'status': 'pending',
        }
    )
    created += 1
    print(f"   Created: {dev.user.email}")

# Update newsletter status
newsletter.status = 'sending'
newsletter.save()
newsletter.update_counts()

print(f"\n✅ Created {created} pending recipient records!")
print(f"   Newsletter status: {newsletter.status}")
print(f"   Pending count: {newsletter.pending_count}")
print(f"\n👉 Next: Go to Admin > Newsletter History > View the newsletter")
print("   Then click 'Start/Resume Sending' to send to remaining recipients.")
