# Customer Portal & Team Management System - Implementation Plan

## Overview
A comprehensive customer portal allowing companies to manage developer teams, view projects, handle contracts, enable billing, and access custom training resources.

---

## Phase 1: Core Team Management & Approval Workflow

### 1.1 Database Models

#### CompanyProfile (New)
```python
- company (OneToOne to Customer) - Link to existing Customer model
- industry
- company_size
- website
- logo
- billing_address
- tax_id
- is_labs_customer (Boolean)
- labs_account_email
- labs_discount_percent (Decimal, default 0)
- created_at
- updated_at
```

#### CompanyAdmin (New)
```python
- company (FK to Customer)
- user (FK to User)
- role (choices: 'owner', 'admin', 'billing', 'viewer')
- can_approve_developers (Boolean)
- can_sign_contracts (Boolean)
- can_manage_billing (Boolean)
- invited_by (FK to User)
- invited_at
- accepted_at
```

#### Notification (New)
```python
- recipient (FK to User or TeamMember)
- notification_type (choices: 'community_approved', 'team_approved', 'contract_signed', 'billing_enabled', etc.)
- title
- message
- link_url
- is_read (Boolean)
- created_at
- related_customer (FK to Customer, nullable)
- related_contract (FK to Contract, nullable)
```

#### Update CustomerDeveloperAssignment
```python
# Add fields:
- approved_by (FK to CompanyAdmin)
- notification_sent (Boolean)
- onboarding_completed (Boolean)
```

#### Update TeamMember
```python
# Add fields:
- community_approval_date
- community_approved_by (FK to User - staff)
- community_approval_notification_sent (Boolean)
```

### 1.2 Approval Workflow

**Developer Community Approval (Staff Admin):**
1. Staff approves TeamMember (sets `approved=True`)
2. System sends email notification
3. System creates in-app notification
4. Developer can now be assigned to customer teams

**Customer Team Approval (Company Admin):**
1. Staff assigns developer to Customer
2. Company Admin reviews and approves/rejects
3. On approval: email + in-app notification to developer
4. Developer gains access to customer portal

### 1.3 Notification System

**Email Templates:**
- `emails/community_approval.html` - Welcome to Buildly Community
- `emails/team_approval.html` - You've been added to {Company} team
- `emails/team_invitation.html` - Invitation to join {Company} team

**In-App Notifications:**
- Bell icon in header with unread count
- Notification panel showing recent notifications
- Mark as read functionality
- Link to relevant resource (team, contract, etc.)

---

## Phase 2: Enhanced Customer Portal

### 2.1 Customer Portal Structure

**URLs:**
```
/customer/register/              - Company registration
/customer/login/                 - Company admin login
/customer/dashboard/             - Main dashboard
/customer/team/                  - Team management
/customer/team/invite/           - Invite company admin
/customer/projects/              - Projects list
/customer/projects/<id>/         - Project detail with Labs/GitHub
/customer/contracts/             - Contracts list
/customer/contracts/<id>/sign/   - Sign contract
/customer/billing/               - Billing overview
/customer/resources/             - Custom resources
/customer/assessments/           - Custom quizzes
/customer/notifications/         - Notifications center
```

### 2.2 Project Management

#### Project Model (New)
```python
- customer (FK to Customer)
- name
- description
- project_type (choices: 'labs', 'custom', 'maintenance')
- labs_url (URL to labs.buildly.dev or labs.buildly.io)
- github_repos (ManyToMany to GitHubRepository)
- assigned_developers (ManyToMany to TeamMember through ProjectDeveloperAssignment)
- start_date
- end_date
- status (choices: 'planning', 'active', 'paused', 'completed')
- created_at
- updated_at
```

#### GitHubRepository (New)
```python
- project (FK to Project)
- repo_url
- repo_name
- repo_owner
- github_token (encrypted)
- last_sync
- stats_cache (JSONField - issues, PRs, commits)
```

#### ProjectDeveloperAssignment (New)
```python
- project (FK to Project)
- developer (FK to TeamMember)
- role (choices: 'lead', 'developer', 'reviewer')
- assigned_at
- removed_at
- is_active
```

### 2.3 GitHub Integration

**Features:**
- Fetch repository stats (commits, PRs, issues)
- Cache stats daily
- Display in project dashboard
- Link to GitHub issues
- Show developer contributions

**Implementation:**
- Use GitHub API v3/GraphQL
- Store encrypted tokens per project
- Background task for daily sync (Celery/Django-Q)

### 2.4 Labs Integration

**Features:**
- Display Labs project URL
- Show Labs account status
- Apply Labs customer discount to billing
- Link to Labs dashboard (if authenticated)

**Implementation:**
- Store Labs URL per project
- Optional: Labs API integration for account verification
- Discount calculation in billing

---

## Phase 3: Contract Management & Billing

### 3.1 Enhanced Contract Model

#### Update Contract
```python
# Add fields:
- contract_type (choices: 'onboarding', 'engagement', 'maintenance')
- billing_enabled (Boolean)
- billing_enabled_by (FK to User - staff)
- billing_enabled_at
- billing_start_date
- billing_end_date
- billing_frequency (choices: 'monthly', 'quarterly', 'custom')
- auto_renew (Boolean)
```

#### ContractLineItem (New)
```python
- contract (FK to Contract)
- item_type (choices: 'training_independent', 'training_agency', 'custom')
- description
- developer (FK to TeamMember, nullable)
- amount (Decimal)
- billing_period_months (Integer)
- start_date
- end_date
- is_recurring (Boolean)
- status (choices: 'pending', 'active', 'paused', 'completed')
```

#### BillingPeriod (New)
```python
- contract (FK to Contract)
- period_start
- period_end
- total_amount
- status (choices: 'pending', 'invoiced', 'paid', 'overdue')
- invoice_date
- payment_date
- stripe_invoice_id (if using Stripe)
```

### 3.2 Billing Configuration

**Training Pricing:**
- Independent Developer: $5,000 over 3 months ($1,666.67/month)
- Agency Developer: $2,500 over 3 months ($833.33/month)
- Engagement: Up to 12 months
- Custom line items for additional services

**Admin Interface:**
- Enable/disable billing per contract
- Add/remove line items
- Set custom amounts
- Apply Labs discount
- Generate invoice preview

**Customer Interface:**
- View billing summary
- See line items breakdown
- Download invoices
- Payment method management (Stripe integration)

### 3.3 Billing Integration with Wave

**Wave API Integration:**
- Create Wave account per customer (or one master account?)
- Auto-create customers/invoices in Wave
- Sync line items from ContractLineItem to Wave Invoice Items
- Track payment status from Wave back to system
- Generate invoices in Wave, link them in Buildly

**Wave Data Flow:**
```
LineItem Created/Updated
→ Sync to Wave Invoice
→ Store Wave Invoice ID
→ Display in Buildly
→ Customer pays in Wave
→ Webhook updates Buildly payment status
```

**Implementation:**
- Use Wave GraphQL API
- Store Wave business ID, customer ID per contract
- Implement Wave webhook handler for payment updates
- Manual invoice generation vs auto-generation (TBD)

---

## Phase 4: Custom Resources & Assessments

### 4.1 Customer-Specific Resources

#### CustomerResource (New)
```python
- customer (FK to Customer)
- resource (FK to Resource)
- is_required (Boolean)
- due_date (nullable)
- created_by (FK to User)
- created_at
```

#### CustomerResourceCompletion (New)
```python
- customer_resource (FK to CustomerResource)
- team_member (FK to TeamMember)
- completed_at
- notes
```

### 4.2 Customer-Specific Quizzes

#### CustomerQuiz (New)
```python
- customer (FK to Customer)
- quiz (FK to Quiz)
- is_required (Boolean)
- passing_score (Integer)
- due_date (nullable)
- created_by (FK to User)
- created_at
```

#### CustomerQuizAttempt (New)
```python
- customer_quiz (FK to CustomerQuiz)
- team_member (FK to TeamMember)
- score (Integer)
- passed (Boolean)
- completed_at
- time_taken (Duration)
```

**Features:**
- Assign resources/quizzes to specific customer teams
- Track completion per developer
- Send reminders for incomplete items
- Generate completion reports

### 4.3 Labs Auth Integration

#### LabsAccount (New)
```python
- team_member (OneToOne to TeamMember)
- labs_username
- labs_email
- labs_token (encrypted)
- labs_user_id
- buildly_profile_linked (Boolean) - One unified profile
- linked_at
- last_sync
- is_active
```

**Features:**
- User logs in with Labs credentials
- Create/link Labs account to Buildly profile
- Store encrypted Labs token
- Sync Labs project access to customer assignments
- Show Labs project URLs in dashboard
- Optional: Pull usage/stats from Labs API

---

## Phase 5: Enhanced Dashboard & Reporting

### 5.1 Customer Dashboard

**Widgets:**
1. Team Overview
   - Total developers
   - Active developers
   - Pending approvals
   - Average assessment score

2. Project Status
   - Active projects
   - GitHub activity (commits this week)
   - Open issues
   - Upcoming milestones

3. Billing Summary
   - Current month charges
   - Next billing date
   - Payment status
   - Outstanding invoices

4. Training Progress
   - Resources completed
   - Quizzes completed
   - Onboarding status per developer

5. Recent Activity
   - Developer approvals
   - Contract signings
   - Project updates
   - Notifications

### 5.2 Admin Dashboard Enhancements

**Super Admin View:**
- All customers overview
- Pending approvals (developers, contracts)
- Billing status across customers
- Revenue projections
- Customer health scores

**Bulk Actions:**
- Approve multiple developers
- Enable billing for multiple contracts
- Send bulk notifications
- Export reports

---

## Implementation Phases & Timeline

### ACCELERATED: Complete by End of Week

#### Phase 1: Foundation & Approvals (Days 1-2)
- [ ] Create new models (CompanyProfile, CompanyAdmin, Notification, LabsAccount)
- [ ] Update existing models (TeamMember, CustomerDeveloperAssignment, Contract)
- [ ] Generate and apply migrations
- [ ] Build notification system (email + in-app with MailerSend)
- [ ] Implement approval workflows (customer approval + global admin assignment)
- [ ] Labs auth integration (login flow, token encryption, linking)
- [ ] Contract signing models and views
- [ ] Email templates (all 3 priority types)
- [ ] Global admin approval center view

#### Phase 2: Customer Portal Core (Days 3-4)
- [ ] Customer registration and admin invitation
- [ ] Customer dashboard layout
- [ ] Team management interface (approve + request removal with 30-day notice)
- [ ] Developer approval interface for customer admins
- [ ] Global admin approval queue (waiting developers)
- [ ] Notification center
- [ ] Labs account linking flow
- [ ] Profile view with Labs integration

#### Phase 3: GitHub & Projects (Days 5 - if time)
- [ ] GitHub token storage (encrypted)
- [ ] GitHub API integration
- [ ] Project management models
- [ ] Project dashboard with stats

#### Billing Phase (After EOW - separate)
- [ ] Manual Wave configuration
- [ ] Invoice status tracking
- [ ] Billing dashboard (read-only for now)

---

## Technical Considerations

### Security
- Role-based access control (RBAC)
- Customer data isolation
- Encrypted GitHub tokens (AES in database)
- Encrypted Labs tokens (AES in database)
- Audit logging for sensitive actions
- Rate limiting on APIs
- CSRF protection on all forms

### Performance
- Database indexing on foreign keys
- Caching for GitHub stats
- Pagination for large lists
- Background tasks for emails and API calls
- CDN for static assets

### Scalability
- Use Celery/Django-Q for async tasks
- Redis for caching and session storage
- PostgreSQL for complex queries
- S3 for contract PDF storage

### Integrations
- **GitHub API**: Repository stats, issues, commits (PAT-based)
- **Labs API**: Account linking, project access, usage stats
- **Wave GraphQL API**: Invoice generation, payment tracking, webhooks
- **Stripe**: Forge marketplace (existing)
- **SendGrid/Mailgun**: Transactional emails
- **Sentry**: Error tracking

---

## Database Schema Summary

### New Models (9)
1. CompanyProfile
2. CompanyAdmin
3. Notification
4. Project
5. GitHubRepository
6. ProjectDeveloperAssignment
7. ContractLineItem
8. BillingPeriod
9. CustomerResource
10. CustomerResourceCompletion
11. CustomerQuiz
12. CustomerQuizAttempt

### Updated Models (3)
1. TeamMember (add community approval fields)
2. CustomerDeveloperAssignment (add approval tracking)
3. Contract (add billing fields)

### Existing Models Used
1. Customer
2. TeamMember
3. DevelopmentAgency
4. Contract
5. Resource
6. Quiz

---

## UI/UX Structure

### Customer Portal Navigation
```
Dashboard
├── Overview
├── Team
│   ├── Developers
│   ├── Pending Approvals
│   └── Invite Admin
├── Projects
│   ├── Active Projects
│   └── Project Detail (Labs, GitHub)
├── Contracts
│   ├── Active Contracts
│   ├── Sign Contract
│   └── Contract History
├── Billing
│   ├── Overview
│   ├── Invoices
│   └── Payment Methods
├── Training
│   ├── Resources
│   └── Assessments
└── Settings
    ├── Company Profile
    ├── Admins
    └── Notifications
```

### Super Admin Portal Enhancement
```
Admin Dashboard
├── Customers
│   ├── All Customers
│   ├── Pending Setups
│   └── Billing Status
├── Approvals
│   ├── Community Members
│   ├── Team Assignments
│   └── Contracts
├── Billing Management
│   ├── Enable Billing
│   ├── Line Items
│   └── Revenue Reports
├── Custom Content
│   ├── Assign Resources
│   └── Assign Quizzes
└── Reports
    ├── Revenue
    ├── Developer Activity
    └── Customer Health
```

---

## API Endpoints (Optional REST API)

```
# Authentication
POST   /api/auth/login/
POST   /api/auth/logout/
POST   /api/auth/refresh/

# Customer
GET    /api/customer/profile/
PATCH  /api/customer/profile/
GET    /api/customer/team/
POST   /api/customer/team/approve/{developer_id}/
GET    /api/customer/projects/
GET    /api/customer/projects/{id}/
GET    /api/customer/contracts/
POST   /api/customer/contracts/{id}/sign/
GET    /api/customer/billing/
GET    /api/customer/notifications/
PATCH  /api/customer/notifications/{id}/read/

# Admin
GET    /api/admin/customers/
POST   /api/admin/developers/{id}/approve/
POST   /api/admin/contracts/{id}/enable-billing/
POST   /api/admin/contracts/{id}/line-items/
GET    /api/admin/reports/revenue/
GET    /api/admin/reports/activity/
```

---

## Decisions Made ✓

1. **GitHub Integration:** ✓
   - Use personal access tokens (user provides token)
   - Display: commits, PRs, issues, contributor stats
   - Tokens encrypted in database
   - Optional webhook integration for real-time updates

2. **Labs Integration:** ✓
   - API docs: https://labs.buildly.io/docs
   - **IN PHASE 1** - included in this week's work
   - User logs in → maps their Labs token auth to Buildly profile
   - Goal: Unified Buildly profile + auth across both platforms
   - Tokens encrypted in database
   - Will evolve as Labs migrates to new version
   - Auto-assign to Labs projects they have access to
   - Manually add project URLs for now (staff)

3. **Billing:** ✓
   - **One master Wave account** (already created)
   - **Manual staff approval** for invoicing (API access pending)
   - Recurring invoice auto-generation (future, once API available)
   - Customer sees billing dates/amounts upfront
   - Wave webhooks for payment status (when API ready)
   - **Billing Phase moved to LAST** (focus on approval workflows first)

4. **Contract Signing:** ✓
   - **MOST URGENT** - electronic signature (typed name + IP + timestamp)
   - PDF generation with signature details
   - Custom implementation (cost-effective)

5. **Notifications - Priority Order:** ✓
   1. Contract signing confirmation
   2. Community approval
   3. Team approval
   4. Billing reminders

6. **Email Service:** ✓
   - MailerSend (already configured in .env)

7. **Approval Workflow:** ✓
   - Customer admins: **approve developers individually** (NOT assign)
   - Developers assigned ONLY by global admin
   - Global admin sees waiting approvals on login
   - Removal: customer requests → global admin processes with **30-day notice**
   - No customer-side reassignment
   - Clear audit trail for all approvals/removals

8. **Permissions:** ✓
   - No cross-customer data visibility
   - Agency admins see their developers across all assigned customers
   - Customer admins see only their company's data
   - Staff sees all data with override capabilities

---

## Next Steps

Please review this plan and provide feedback on:
1. Priority of phases (any changes?)
2. Answers to questions above
3. Any features to add/remove
4. Timeline expectations
5. Technical preferences (Stripe vs other, GitHub approach, etc.)

Once approved, I'll begin implementation starting with Phase 1.
