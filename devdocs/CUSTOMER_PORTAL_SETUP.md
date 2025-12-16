# Customer Portal - Quick Setup Guide

## Initial Setup (5 minutes)

### 1. Create Your First Customer

```bash
# Access Django Admin
# Navigate to: http://localhost:8000/admin/onboarding/customer/

# Click "Add Customer" and fill in:
```

**Example Customer:**
- Company Name: `Acme Corporation`
- Contact Name: `Jane Smith`
- Contact Email: `jane@acme.com`
- Contact Phone: `(555) 123-4567`
- Username: `acme_jane`
- Password: `demo123` (change in production!)
- Is Active: ✓ (checked)

**Assign Developers:**
- Select 2-3 developers from the list

Click **Save**

### 2. Create a Sample Contract

```bash
# Navigate to: http://localhost:8000/admin/onboarding/contract/
# Click "Add Contract"
```

**Example Contract:**
- Customer: `Acme Corporation (Jane Smith)`
- Title: `Q1 2025 Development Engagement`
- Contract Text:
```
ENGAGEMENT AGREEMENT

This agreement is entered into between Buildly and Acme Corporation.

SCOPE OF WORK:
The developers assigned to this project will provide full-stack development services for a period of 3 months.

TERMS:
- Start Date: January 1, 2025
- End Date: March 31, 2025
- Hourly Rate: $95/hour
- Estimated Hours: 480 hours (40 hours/week × 12 weeks)
- Total Estimated Cost: $45,600

DELIVERABLES:
- Web application development
- API integration
- Code documentation
- Weekly progress reports

PAYMENT TERMS:
Invoices will be submitted bi-weekly with net-30 payment terms.

By signing this agreement, you authorize Buildly to begin work as described above.
```
- Start Date: `2025-01-01`
- End Date: `2025-03-31`
- Hourly Rate: `95.00`
- Status: `Pending`
- Developers: Select the same developers assigned to the customer

Click **Save**

### 3. Test the Portal

**Customer Login:**
1. Navigate to: `http://localhost:8000/onboarding/client/login/`
2. Username: `acme_jane`
3. Password: `demo123`
4. Click "Sign In"

**You should see:**
- Dashboard with 2-3 assigned developers
- 1 pending contract
- Quick stats overview

**Test Developer Profile:**
1. Click "View Full Profile" on any developer
2. Review their information, skills, and assessment scores

**Test Contract Signing:**
1. Go back to Dashboard
2. Click "View Contract" on the pending contract
3. Click "Sign Contract Now"
4. Enter your name: `Jane Smith`
5. Draw signature in the canvas
6. Check the agreement checkbox
7. Click "Sign and Submit Contract"
8. Verify status changes to "Signed"

## Production Deployment

### Security Improvements

**1. Hash Customer Passwords**

Update `Customer` model's `check_password()` method:
```python
from django.contrib.auth.hashers import make_password, check_password as check_hash

class Customer(models.Model):
    # ... other fields
    password = models.CharField(max_length=255)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_hash(raw_password, self.password)
```

**2. Environment Variables**

Add to `.env`:
```bash
CUSTOMER_SESSION_TIMEOUT=3600  # 1 hour
CUSTOMER_PASSWORD_MIN_LENGTH=12
```

**3. HTTPS Only**

Update settings:
```python
# In production settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### Email Notifications

**Install packages:**
```bash
pip install django-templated-email
```

**Create email templates** in `onboarding/templates/emails/`:
- `contract_ready.html` - Notify customer contract is ready
- `contract_signed.html` - Confirm signature received

**Update views to send emails:**
```python
from django.core.mail import send_mail

# In admin_create_contract view:
send_mail(
    'Contract Ready for Signature',
    f'Your contract "{contract.title}" is ready for review and signature.',
    'noreply@buildly.com',
    [customer.contact_email],
    fail_silently=True,
)
```

## Common Admin Tasks

### Add New Customer
```bash
Admin → Customers → Add Customer
```

### Assign More Developers
```bash
Admin → Customers → Select Customer → Edit
# Scroll to "Assigned Developers"
# Ctrl+Click to select multiple
# Save
```

### Create New Contract
```bash
Admin → Contracts → Add Contract
# Select customer
# Fill in terms
# Assign developers
# Set status to "Pending"
# Save
```

### View Signed Contracts
```bash
Admin → Contracts → Filter by Status: "Signed"
# View signature_data, signed_by, signed_at
```

### Deactivate Customer Access
```bash
Admin → Customers → Select Customer → Edit
# Uncheck "Is Active"
# Save
# Customer can no longer login
```

## Integration with Existing Features

### Link to Assessment System
The portal automatically displays:
- Assessment completion status (`has_completed_assessment`)
- Assessment scores from `QuizAnswer` model
- Last completed date from `assessment_completed_at`

### Link to Learning Resources
Shows developer progress on assigned resources via `TeamMemberResource` model:
- Resource title
- Completion percentage
- Progress bar visualization

### Link to Quiz System
Displays recent quiz answers:
- Question text
- Developer's answer
- Correct/incorrect for MC questions
- Evaluator scores for essay questions

## Troubleshooting

### "No developers assigned yet"
- Verify customer has assigned_developers in admin
- Ensure developers have `approved=True`

### "Overall Score: 0%"
- Developer hasn't completed any assessments
- Check QuizAnswer records exist
- Verify evaluator_score is set for essays

### Signature pad not working
- Check browser console for errors
- Verify JavaScript is enabled
- Test on different browser (Chrome recommended)

### Cannot login
- Verify `is_active=True` in admin
- Check username/password are correct
- Clear browser cookies and try again

## Next Steps

1. ✅ Create 2-3 test customers
2. ✅ Assign different developers to each
3. ✅ Create sample contracts
4. ✅ Test full signing workflow
5. ✅ Review signed contract display
6. ✅ Test on mobile devices
7. ✅ Share portal URL with real customers

## Support

For questions or issues:
- Check `/devdocs/CUSTOMER_PORTAL.md` for full documentation
- Review Django admin logs
- Check application logs for errors
- Contact development team

---

**Quick Links:**
- Customer Login: `/onboarding/client/login/`
- Django Admin: `/admin/onboarding/customer/`
- Contracts Admin: `/admin/onboarding/contract/`
