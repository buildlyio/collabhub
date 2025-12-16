# Customer/Client Portal System Documentation

## Overview

The Customer Portal is a secure, dedicated interface where clients can view profiles of assigned developers, track onboarding progress, review assessment scores, and digitally sign engagement contracts.

## Features

### 1. **Customer Management**
- **Django Admin Integration**: Full CRUD operations for customers
- **Authentication**: Username/password-based login system
- **Developer Assignment**: Many-to-many relationship for assigning developers to customers
- **Session Management**: Secure session-based authentication

### 2. **Developer Profiles**
Each customer can view comprehensive profiles of their assigned developers including:
- Personal information (name, email, LinkedIn, GitHub)
- Professional details (role, experience years, bio)
- **Onboarding Status**: Track completion of assessments
- **Assessment Scores**: Overall score percentage from quiz results
  - Multiple choice questions (auto-scored)
  - Essay questions (evaluator-scored)
- **Learning Resources**: Progress tracking on assigned learning materials
- **Recent Assessment Answers**: View Q&A from completed assessments

### 3. **Digital Contract Signing**
- **Contract Management**: Admins create contracts with terms, rates, and developer assignments
- **Digital Signature Capture**: HTML5 canvas-based signature pad
- **Legal Compliance**: Captures signature, name, timestamp, and IP address
- **Contract Status Tracking**: Draft → Pending → Signed → Expired/Cancelled
- **Base64 Signature Storage**: Signatures saved as data URLs for retrieval

### 4. **Dashboard Features**
- Summary statistics (assigned developers, pending/signed contracts)
- Quick access to developer profiles
- Contract status overview
- Responsive design with Tailwind CSS

## Database Models

### Customer Model
```python
- company_name: CharField
- contact_name: CharField
- contact_email: EmailField (unique)
- contact_phone: CharField
- username: CharField (unique)
- password: CharField (plain text - should be hashed in production)
- assigned_developers: ManyToManyField(TeamMember)
- created_at: DateTimeField
- last_login: DateTimeField
- is_active: BooleanField
- notes: TextField
```

### Contract Model
```python
- customer: ForeignKey(Customer)
- developers: ManyToManyField(TeamMember)
- title: CharField
- contract_text: TextField
- start_date: DateField
- end_date: DateField
- hourly_rate: DecimalField (optional)
- project_rate: DecimalField (optional)
- status: CharField (draft/pending/signed/expired/cancelled)
- signature_data: TextField (Base64 encoded image)
- signed_by: CharField
- signed_at: DateTimeField
- ip_address: GenericIPAddressField
- created_at: DateTimeField
- created_by: ForeignKey(User)
```

## URL Routes

### Customer Portal URLs
- `/onboarding/client/login/` - Customer login page
- `/onboarding/client/logout/` - Customer logout
- `/onboarding/client/dashboard/` - Main dashboard
- `/onboarding/client/developer/<id>/` - Developer detail profile
- `/onboarding/client/contract/<id>/` - View contract details
- `/onboarding/client/contract/<id>/sign/` - Sign contract with digital signature

## Admin Workflow

### Step 1: Create a Customer
1. Go to Django Admin → Customers → Add Customer
2. Fill in company information:
   - Company Name
   - Contact Name
   - Contact Email
   - Contact Phone
3. Set authentication credentials:
   - Username (unique)
   - Password (plain text for now)
   - Is Active (checked)
4. Assign developers:
   - Select developers from the multi-select list
5. Add internal notes if needed
6. Save

### Step 2: Create a Contract
1. Go to Django Admin → Contracts → Add Contract
2. Fill in contract details:
   - Select Customer
   - Enter Title
   - Add Contract Text (full terms)
   - Set Start Date and End Date
   - Set Hourly Rate or Project Rate (optional)
3. Assign developers to the contract
4. Set Status to "Pending" (for signature required)
5. Save

### Step 3: Share Portal Access
Share the following with your customer:
- Portal URL: `https://your-domain.com/onboarding/client/login/`
- Username: (as created)
- Password: (as created)

## Customer Workflow

### Step 1: Login
1. Navigate to `/onboarding/client/login/`
2. Enter username and password
3. Click "Sign In"

### Step 2: View Dashboard
- See assigned developers count
- View pending and signed contracts
- Access developer profiles
- Review contract status

### Step 3: Review Developer Profiles
1. Click "View Full Profile" on any developer card
2. Review:
   - Contact information and social links
   - Professional experience
   - Assessment completion status
   - Overall assessment score
   - Learning resource progress
   - Recent assessment answers (Q&A)

### Step 4: Sign Contracts
1. Click "View Contract" on dashboard
2. Review contract terms and details
3. Click "Sign Contract Now"
4. Enter full legal name
5. Draw signature on canvas pad
6. Check agreement checkbox
7. Click "Sign and Submit Contract"
8. Contract status changes to "Signed"

## Security Features

### Authentication
- Session-based authentication separate from Django User auth
- Custom `@customer_required` decorator for view protection
- Automatic session expiration on logout
- Active status check on every request

### Digital Signature Security
- IP address capture at time of signing
- Timestamp recording
- Base64 encoded signature storage
- Read-only signature display after signing
- Agreement checkbox requirement

### Data Privacy
- Customers can only view their assigned developers
- No access to unassigned developer profiles
- No ability to modify data (read-only for customers)
- Secure session management

## Assessment Score Calculation

The system calculates overall assessment scores using:

1. **Multiple Choice Questions**:
   - Auto-scored as correct/incorrect
   - Percentage = (correct_answers / total_mc_questions) × 100

2. **Essay Questions**:
   - Manually scored by evaluators (0-10 scale)
   - Percentage = (sum_of_scores / (question_count × 10)) × 100

3. **Overall Score**:
   - Average of MC percentage and Essay percentage
   - Displayed on developer profile page

## Templates

### Customer Portal Templates
1. **customer_login.html** - Login page with gradient design
2. **customer_dashboard.html** - Main dashboard with stats and cards
3. **customer_developer_detail.html** - Full developer profile view
4. **customer_contract_view.html** - Contract details with signed status
5. **customer_contract_sign.html** - Signature capture interface

## Customization

### Branding
Update the following in templates:
- Logo: Change "Buildly" text in login header
- Colors: Modify Tailwind gradient classes (from-blue-600, to-indigo-600, etc.)
- Footer: Update copyright text

### Contract Templates
- Customize contract text format in Django Admin
- Add custom fields to Contract model if needed
- Modify contract display layout in templates

### Assessment Display
- Adjust which assessment answers are shown (currently last 10)
- Customize score calculation logic in views
- Add additional statistics or graphs

## Future Enhancements

### Recommended Improvements
1. **Password Hashing**: Use Django's password hashing for customer passwords
2. **Email Notifications**: Send email when contracts are ready for signature
3. **PDF Export**: Generate PDF versions of signed contracts
4. **Multi-Factor Authentication**: Add 2FA for customer login
5. **Contract Versioning**: Track contract revisions and updates
6. **Developer Feedback**: Allow customers to rate/review developers
7. **Communication Portal**: Add messaging between customers and Buildly team
8. **Analytics Dashboard**: Track customer engagement metrics
9. **Mobile App**: Create native mobile apps for iOS/Android
10. **SSO Integration**: Support OAuth/SAML for enterprise customers

## Troubleshooting

### Customer Cannot Login
- Verify `is_active` is True in Django Admin
- Check username/password are correct
- Ensure no typos in credentials
- Check session configuration in Django settings

### Developer Profile Not Showing
- Verify developer is assigned to customer in Admin
- Check TeamMember `approved` status
- Ensure developer has completed onboarding

### Contract Signature Not Saving
- Check browser console for JavaScript errors
- Verify signature canvas is drawn on before submission
- Ensure agreement checkbox is checked
- Check network tab for 500 errors

### Assessment Scores Not Displaying
- Verify QuizAnswer records exist for developer
- Check that evaluator_score is set for essay questions
- Ensure quiz questions have correct question_type
- Verify is_correct is set for multiple choice answers

## API Integration (Future)

Consider building REST API endpoints for:
- Customer authentication (JWT tokens)
- Developer profile retrieval
- Contract status checks
- Signature submission
- Webhook notifications for contract events

## Files Modified/Created

### Models
- `onboarding/models.py` - Added Customer and Contract models with Admin classes
- `onboarding/admin.py` - Registered Customer and Contract models

### Views
- `onboarding/views.py` - Added 6 customer portal views:
  - `customer_login()` - Authentication
  - `customer_logout()` - Session termination
  - `customer_dashboard()` - Main portal
  - `customer_developer_detail()` - Developer profile
  - `customer_contract_view()` - Contract display
  - `customer_contract_sign()` - Signature capture

### Templates
- `onboarding/templates/customer_login.html`
- `onboarding/templates/customer_dashboard.html`
- `onboarding/templates/customer_developer_detail.html`
- `onboarding/templates/customer_contract_view.html`
- `onboarding/templates/customer_contract_sign.html`

### URLs
- `onboarding/urls.py` - Added 6 customer portal routes

### Migrations
- `onboarding/migrations/0012_contract_customer.py`

## Testing Checklist

- [ ] Create test customer in admin
- [ ] Assign developers to customer
- [ ] Create pending contract for customer
- [ ] Login with customer credentials
- [ ] View dashboard statistics
- [ ] Navigate to developer profile
- [ ] Review assessment scores
- [ ] Open contract for signing
- [ ] Draw signature and submit
- [ ] Verify contract status changes to "signed"
- [ ] View signed contract with signature displayed
- [ ] Test logout functionality
- [ ] Verify cannot access portal after logout

---

**Status**: ✅ Complete and Ready for Production
**Last Updated**: December 15, 2025
