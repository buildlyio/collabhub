# Phase 1: Implementation Checklist - END OF WEEK

## Models to Create/Update

### NEW MODELS
- [ ] CompanyProfile
- [ ] CompanyAdmin  
- [ ] Notification
- [ ] LabsAccount

### UPDATE MODELS
- [ ] TeamMember (add: `community_approval_date`, `community_approved_by`, `community_approval_notification_sent`)
- [ ] CustomerDeveloperAssignment (add: `approved_by`, `notification_sent`)
- [ ] Contract (add: `contract_type`, `signed_at`, `signed_by`, `signature_ip`, `signature_timestamp`)

## Views/URLs to Create

### Authentication & Auth Integration
- [ ] `/onboarding/labs/login/` - Labs login redirect + token exchange
- [ ] `/onboarding/labs/callback/` - Labs OAuth callback
- [ ] `/onboarding/labs/link/` - Link existing Labs account
- [ ] `/onboarding/labs/unlink/` - Unlink Labs account

### Approvals Workflow
- [ ] `/customer/team/approve/<developer_id>/` - Customer approves developer (POST)
- [ ] `/customer/team/request-removal/<developer_id>/` - Request 30-day removal (POST)
- [ ] `/admin/approvals/` - Global admin approval queue (GET with list)
- [ ] `/admin/approvals/assign/<developer_id>/` - Admin assigns developer (POST)
- [ ] `/admin/approvals/removal/<request_id>/process/` - Admin processes removal (POST)

### Contract Signing
- [ ] `/customer/contracts/<contract_id>/sign/` - Sign contract form (GET)
- [ ] `/customer/contracts/<contract_id>/sign/submit/` - Submit signature (POST)
- [ ] `/customer/contracts/<contract_id>/pdf/` - Download signed PDF

### Notifications
- [ ] `/customer/notifications/` - Notification center (GET)
- [ ] `/api/notifications/mark-read/` - Mark as read (POST)
- [ ] `/api/notifications/unread-count/` - Get unread count (GET)

## Email Templates to Create

- [ ] `emails/community_approval.html` - Developer approved to Buildly community
- [ ] `emails/team_approval.html` - Developer approved to customer team  
- [ ] `emails/team_removal_requested.html` - Admin notified of removal request
- [ ] `emails/removal_30day_notice.html` - Developer gets 30-day removal notice
- [ ] `emails/contract_ready_sign.html` - Contract is ready to sign
- [ ] `emails/contract_signed_confirmation.html` - Contract signed confirmation

## Utilities & Helper Functions

- [ ] Encryption utility (encrypt/decrypt tokens)
- [ ] Token generation for password reset/email verification
- [ ] PDF generation for contract signing
- [ ] MailerSend email service wrapper

## Admin Interface Updates

- [ ] TeamMember admin - show approval status + buttons
- [ ] CustomerDeveloperAssignment admin - show approval status
- [ ] New Notification admin
- [ ] New LabsAccount admin

## Tasks/Signals

- [ ] Signal: When TeamMember.approved changes → send community approval email
- [ ] Signal: When CustomerDeveloperAssignment status changes → send team approval email
- [ ] Signal: When removal requested → notify admin
- [ ] Background task: 30-day removal countdown reminders

## Testing

- [ ] Unit tests for approval workflow
- [ ] Integration tests for email sending
- [ ] Manual testing of Labs auth flow
- [ ] Manual testing of approval workflows

---

## Ready to Start?

**I will begin Phase 1 with:**

1. **Models** (onboarding/models.py)
   - CompanyProfile, CompanyAdmin, Notification, LabsAccount
   - Update TeamMember, CustomerDeveloperAssignment, Contract
   - Add helper methods + __str__

2. **Migrations** (onboarding/migrations/)
   - Generate migration file
   - Note: You'll need to apply on server

3. **Views** (onboarding/views.py)
   - Labs auth integration
   - Approval workflows (customer + admin)
   - Contract signing
   - Notification center

4. **URLs** (onboarding/urls.py)
   - Add all new URL patterns

5. **Email Templates** (onboarding/templates/emails/)
   - HTML email templates

6. **Utilities** (onboarding/utils.py - NEW FILE)
   - Encryption helpers
   - Email sending wrapper
   - PDF generation

7. **Admin** (onboarding/admin.py)
   - Register new models
   - Customizations

**Proceed? (Y/N)**
