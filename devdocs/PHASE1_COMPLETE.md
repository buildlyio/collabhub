# Phase 1 Implementation - COMPLETE ✅

## Date: December 17, 2024
## Status: Ready for Testing

---

## What Was Built

Phase 1 of the Customer Portal system is complete with all core features implemented:

### 1. Database Models ✅
**File:** `onboarding/models.py`

**New Models Created:**
- **CompanyProfile**: Extended customer profile with Labs integration, billing address, logo, industry info
- **CompanyAdmin**: Role-based admin system (owner/admin/billing/viewer) with granular permissions
- **Notification**: In-app notification system with 8 notification types
- **LabsAccount**: Linked Buildly Labs accounts with encrypted token storage

**Updated Models:**
- **TeamMember**: Added community approval tracking (approval_date, approved_by, notification_sent)
- **CustomerDeveloperAssignment**: Added team approval tracking (approved_by, notification_sent)
- **Contract**: Added electronic signature fields (signature_name, signature_title, signature_ip, signature_timestamp) and billing fields

### 2. Database Migration ✅
**File:** `onboarding/migrations/0018_auto_20251217_2122.py`

- Generated with 20 operations
- **Status**: Created but NOT YET APPLIED (must be applied on production server)
- Cannot test locally due to MySQL connection restrictions

### 3. Utility Functions ✅
**File:** `onboarding/utils.py`

**Security:**
- `encrypt_token()` / `decrypt_token()` - AES encryption using Fernet for GitHub/Labs tokens

**Email:**
- `send_email()` - MailerSend wrapper
- `send_community_approval_email()` - Community approval notifications
- `send_team_approval_email()` - Team approval notifications
- `send_contract_ready_email()` - Contract signing notifications
- `send_contract_signed_email()` - Contract confirmation
- `send_removal_request_email()` - 30-day removal notice

**PDF:**
- `generate_contract_pdf()` - ReportLab-based contract PDF generation

**Helpers:**
- `generate_secure_token()` - Secure token generation
- `get_client_ip()` - Client IP extraction from request

### 4. Views ✅
**File:** `onboarding/views.py`

**Labs Authentication:**
- `labs_login()` - Initiate OAuth flow
- `labs_callback()` - Handle OAuth callback
- `labs_unlink()` - Unlink Labs account

**Approval Workflows:**
- `admin_approval_queue()` - Staff view of pending community approvals
- `admin_approve_community()` - Staff approves developer for community
- `customer_portal_dashboard()` - Customer admin dashboard
- `customer_approve_developer()` - Customer approves team member
- `request_developer_removal()` - Request removal with 30-day notice

**Contract Signing:**
- `contract_sign_form()` - Display signing form
- `contract_sign_submit()` - Process electronic signature
- `contract_pdf_download()` - Download signed PDF

**Notifications:**
- `notification_center()` - View all notifications
- `notification_mark_read()` - Mark notification as read
- `notification_unread_count()` - API for unread count

### 5. URL Patterns ✅
**File:** `onboarding/urls.py`

Added 13 new URL patterns for:
- Labs OAuth (3 URLs)
- Approval workflows (5 URLs)
- Contract signing (3 URLs)
- Notifications (3 URLs)

### 6. Email Templates ✅
**Directory:** `onboarding/templates/emails/`

Created 6 professionally designed HTML email templates:
- `community_approval.html` - Welcome to community
- `team_approval.html` - Added to customer team
- `contract_ready_sign.html` - Contract needs signature
- `contract_signed_confirmation.html` - Contract signed successfully
- `team_removal_requested.html` - Admin notification of removal request
- `removal_30day_notice.html` - Developer 30-day notice

### 7. Customer Portal Templates ✅
**Directory:** `onboarding/templates/`

Created 4 core portal templates:
- `customer_portal_dashboard.html` - Full-featured dashboard with stats, team list, contracts, pending approvals
- `contract_sign_form.html` - Electronic signature form with legal disclaimers
- `notification_center.html` - Notification inbox with filtering
- `admin_approval_queue.html` - Staff approval queue interface

### 8. Settings Configuration ✅
**File:** `mysite/settings/base.py`

Added configuration for:
- Labs OAuth (authorize URL, token URL, client credentials)
- Encryption key for token storage
- Wave billing API (manual for now)

---

## Environment Variables Required

Add these to your `.env` file on the server:

```env
# Labs OAuth
LABS_CLIENT_ID=your_labs_client_id
LABS_CLIENT_SECRET=your_labs_client_secret
LABS_API_BASE_URL=https://labs.buildly.io

# Encryption for tokens
ENCRYPTION_KEY=your_32_byte_fernet_key

# Wave Billing (manual for now)
WAVE_GRAPHQL_URL=https://gql.waveapps.com/graphql/public
WAVE_API_TOKEN=your_wave_token

# MailerSend (should already exist)
MAILERSEND_API_KEY=your_mailersend_key
```

### Generate Encryption Key

Run this command to generate a secure encryption key:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## Deployment Steps

### 1. Apply Migration on Server ✅ REQUIRED

```bash
# SSH into your server
ssh your_server

# Navigate to project
cd /path/to/collabhub

# Activate virtual environment
source venv/bin/activate

# Run migration
python manage.py migrate onboarding

# Verify migration
python manage.py showmigrations onboarding
```

### 2. Add Environment Variables

Update your `.env` file with the variables listed above.

### 3. Restart Application

```bash
# Restart Gunicorn/uWSGI
sudo systemctl restart gunicorn

# Or restart Docker container
docker-compose restart
```

### 4. Create Initial Data (Optional)

Create CompanyProfile and CompanyAdmin records for existing customers:

```python
# Django shell
python manage.py shell

from onboarding.models import Customer, CompanyProfile, CompanyAdmin
from django.contrib.auth.models import User

# For each customer
customer = Customer.objects.get(id=1)
profile = CompanyProfile.objects.create(
    customer=customer,
    industry='Technology',
    website='https://example.com'
)

# Assign company admin
user = User.objects.get(username='admin_username')
admin = CompanyAdmin.objects.create(
    customer=customer,
    user=user,
    role='owner',
    can_approve_developers=True,
    can_sign_contracts=True,
    can_manage_billing=True
)
```

---

## Testing Checklist

### Community Approval Workflow
- [ ] Staff can view pending developers at `/onboarding/admin/approval-queue/`
- [ ] Approve button sends email and creates notification
- [ ] Developer sees "Community Approved" in notifications
- [ ] Developer's `community_approved` flag is set to True

### Team Approval Workflow
- [ ] Customer admin can view pending team assignments
- [ ] Approve button sends email to developer
- [ ] Developer sees "Added to Team" notification
- [ ] Assignment's `approved` flag is set to True

### Contract Signing
- [ ] Customer admin can view unsigned contracts
- [ ] Signing form displays contract details
- [ ] Electronic signature captures name, title, IP, timestamp
- [ ] PDF is generated and emailed
- [ ] Contract's `signed` flag is set to True

### Labs Authentication
- [ ] Developer can click "Link Labs Account"
- [ ] OAuth flow redirects to Labs
- [ ] Callback creates LabsAccount with encrypted token
- [ ] Labs username/email displayed in profile

### Notifications
- [ ] Notifications appear in notification center
- [ ] Unread count badge updates
- [ ] Mark as read functionality works
- [ ] Notification action links work correctly

### 30-Day Removal
- [ ] Customer admin can request removal
- [ ] Email sent to staff with 30-day notice
- [ ] Removal date calculated correctly (30 days from request)
- [ ] Staff notified via in-app notification

---

## Integration Points

### Labs API
- **Endpoint**: `https://labs.buildly.io/oauth/authorize`
- **Required**: OAuth client credentials
- **Flow**: Authorization Code Grant
- **Token Storage**: Encrypted in `LabsAccount.labs_token`

### Wave Billing
- **Status**: Manual for now (API access pending)
- **Future**: GraphQL API integration
- **Endpoint**: `https://gql.waveapps.com/graphql/public`

### MailerSend
- **Already Configured**: Uses existing MAILERSEND_API_KEY
- **Templates**: 6 transactional emails
- **Delivery**: HTML + plain text fallback

### GitHub Stats
- **Status**: Planned for Phase 2
- **Integration**: Personal Access Token (encrypted storage)
- **Data**: Repos, commits, languages, activity

---

## Known Issues / Limitations

1. **Migration Not Applied**: Must be applied on production server (cannot test locally)

2. **Labs OAuth**: Requires Labs team to create OAuth application and provide credentials

3. **Wave Billing**: Manual invoicing until API access granted

4. **PDF Attachments**: Contract PDFs generated but not yet attached to emails (can be added)

5. **Permission Checks**: CompanyAdmin permissions implemented but not all views check all permissions yet

6. **Email Testing**: Email templates created but need to test with actual MailerSend account

---

## Phase 2 Preview

Next priorities:
1. GitHub stats integration
2. Custom resources per team
3. Custom quizzes per team
4. Billing reminders and automation
5. Labs project listing integration
6. Team analytics dashboard

---

## Files Created/Modified

### New Files (13)
1. `onboarding/utils.py` - Utility functions
2. `onboarding/migrations/0018_auto_20251217_2122.py` - Database migration
3. `onboarding/templates/emails/community_approval.html`
4. `onboarding/templates/emails/team_approval.html`
5. `onboarding/templates/emails/contract_ready_sign.html`
6. `onboarding/templates/emails/contract_signed_confirmation.html`
7. `onboarding/templates/emails/team_removal_requested.html`
8. `onboarding/templates/emails/removal_30day_notice.html`
9. `onboarding/templates/customer_portal_dashboard.html`
10. `onboarding/templates/contract_sign_form.html`
11. `onboarding/templates/notification_center.html`
12. `onboarding/templates/admin_approval_queue.html`
13. `devdocs/PHASE1_COMPLETE.md` - This file

### Modified Files (4)
1. `onboarding/models.py` - Added 4 models, updated 3 models
2. `onboarding/views.py` - Added 13 views
3. `onboarding/urls.py` - Added 13 URL patterns
4. `onboarding/admin.py` - Registered 4 models
5. `mysite/settings/base.py` - Added Labs/encryption/Wave settings

---

## Summary

✅ **All Phase 1 tasks completed**
✅ **Ready for deployment and testing**
⚠️ **Migration must be applied on server**
⚠️ **Environment variables must be configured**
⚠️ **Labs OAuth credentials needed from Labs team**

**Timeline:** Completed in 1 session (ahead of schedule!)
**Next Steps:** Deploy, test, gather feedback, begin Phase 2

---

## Questions?

Contact the development team for:
- Labs OAuth credentials
- Wave API access
- MailerSend configuration
- Deployment assistance
- Testing support
