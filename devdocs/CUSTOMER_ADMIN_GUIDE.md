# Customer Admin Dashboard Guide

## Overview

The Customer Admin Dashboard provides a centralized interface for managing customer accounts, assigning developers, and generating shareable links for customer approval workflows.

## Accessing the Customer Admin

1. Navigate to Django Admin: `http://localhost:8000/admin`
2. Click on **"Customers"** under the Onboarding section
3. Select a customer to view/edit

## Key Features

### 1. **Developer Assignment & Management**

When editing a customer, you'll see an inline table at the bottom labeled **"Customer developer assignments"**:

#### Adding Developers
- Click the **"Developer"** dropdown in the inline table
- Select a team member from the list
- Status defaults to **"Pending Review"**
- Click **"Save"** to assign the developer

#### Viewing Developer Profiles
- Each assigned developer has a **"📋 View Full Profile"** link
- Click this to open the developer's full admin profile in a new tab
- View their:
  - Bio, experience, and contact information
  - Assessment scores and completed quizzes
  - Learning resources and progress
  - GitHub, LinkedIn, and other accounts

#### Approval Status Tracking
The admin displays three statuses:
- **Pending Review** ⏳ - Awaiting customer decision
- **Approved** ✓ - Customer has approved this developer
- **Rejected** ✗ - Customer has declined this developer

Status is automatically updated when customers use the shareable link.

### 2. **Shareable Link Generation**

#### Auto-Generation
- Share tokens are **automatically generated** when you save a new customer
- The shareable URL appears in the **"Shareable Access"** section

#### Manual Generation
If a customer doesn't have a token:

1. Go to the Customer list view
2. Select one or more customers (checkbox)
3. Use the **"Actions"** dropdown
4. Choose **"🔗 Generate share token (for customers without one)"**
5. Click **"Go"**

#### Regenerating Tokens
To invalidate an old link and create a new one:

1. Select the customer(s)
2. Choose **"🔄 Regenerate share token (invalidates old link)"**
3. Click **"Go"**
4. ⚠️ **Warning**: Old links will stop working

### 3. **Customer Dashboard Stats**

The list view shows:
- **Company Name** - Customer organization
- **Contact Name** - Primary contact person
- **Contact Email** - Email address
- **Username** - Login username (optional)
- **Has Token** - ✓ or ✗ indicator
- **Developer Count** - Shows: `X total (✓Y ⏳Z ✗W)`
  - X = Total assigned developers
  - Y = Approved count
  - Z = Pending count
  - W = Rejected count
- **Is Active** - Whether customer can log in
- **Created At** - Account creation date

### 4. **Shareable URL Details**

#### What It Looks Like
```
http://yourdomain.com/onboarding/client/shared/abc123...xyz789/
```

#### What Customers Can Do (No Login Required)
1. **View Dashboard** - See all assigned developers with stats
2. **Review Profiles** - Click to see full developer details including:
   - Professional experience
   - Assessment scores (MC and Essay)
   - Detailed quiz answers
   - Completed learning resources
3. **Approve/Reject** - Make decisions on each developer
4. **Sign Contracts** - Digitally sign engagement contracts

#### Security Features
- **48-byte token** (highly secure, URL-safe)
- **Unique per customer** - Each customer gets their own link
- **No login required** - Frictionless access
- **IP tracking** - Records who signs contracts
- **Timestamp tracking** - Records when decisions are made

### 5. **Contract Management**

Within the Customer admin, you can create contracts:

1. Click **"Add Another Contract"** in the Contracts section
2. Fill in:
   - Title
   - Contract text
   - Start/End dates
   - Hourly or project rate
   - Select assigned developers
3. Set status to **"Pending Signature"**
4. Customer will see this in their shareable dashboard

## Workflow Example

### Setting Up a New Customer

1. **Create Customer**
   ```
   Admin → Customers → Add Customer
   - Company Name: "Acme Corp"
   - Contact Name: "John Smith"
   - Contact Email: "john@acme.com"
   - Username: "acme_john" (optional)
   ```

2. **Assign Developers**
   - Scroll to "Customer developer assignments" section
   - Add 3 developers using the inline form
   - Click "Save"

3. **Copy Shareable Link**
   - After saving, copy the URL from "Shareable Access" section
   - Looks like: `http://localhost:8000/onboarding/client/shared/abc123.../`

4. **Send to Customer**
   - Email the link to john@acme.com
   - Customer clicks link (no login needed)
   - Customer sees dashboard with 3 developers

5. **Customer Takes Action**
   - Reviews each developer profile
   - Approves 2 developers
   - Rejects 1 developer
   - Signs the contract

6. **Check Results**
   - Back in admin, reload the customer page
   - Developer Count shows: `3 total (✓2 ⏳0 ✗1)`
   - Click individual assignment rows to see customer notes
   - Contract shows status: "Signed"

## Admin Actions Reference

### List View Actions

| Action | Description | When to Use |
|--------|-------------|-------------|
| 🔗 Generate share token | Creates tokens for customers without one | First time setup |
| 🔄 Regenerate share token | Creates new token, invalidates old | Security: link was shared incorrectly |

### Detail View Sections

| Section | Purpose | Key Fields |
|---------|---------|------------|
| Company Information | Basic customer details | Company name, contact info |
| Authentication | Login credentials (optional) | Username, password, is_active |
| Shareable Access | Passwordless link for customers | Shareable URL display |
| Customer Developer Assignments | Manage assigned developers | Developer, status, profile link, notes |
| Metadata | System tracking info | Created at, last login, internal notes |

## Troubleshooting

### No "Generate share token" action visible
**Solution**: The actions dropdown is at the bottom of the customer list page. Select at least one customer first.

### Link shows "Invalid token"
**Cause**: Token was regenerated or customer was deleted
**Solution**: Generate a new token using the "Regenerate share token" action

### Can't see developer profiles
**Cause**: Inline form link not visible
**Solution**: Save the customer first to create the assignment, then the profile link appears

### Customer hasn't approved/rejected
**Check**: 
1. Did they receive the correct shareable link?
2. Is the customer account active? (is_active=True)
3. Check the shareable URL in a browser to confirm it loads

### Want to change assigned developers
**Solution**: 
1. In the inline table, change the developer dropdown
2. Or delete the row (checkbox + delete)
3. Save the customer

## Best Practices

### ✅ Do
- Generate share tokens immediately after creating customers
- Send shareable links via secure email
- Monitor approval status regularly
- Add internal notes to track customer interactions
- Use the profile links to verify developer information before sending

### ❌ Don't
- Share tokens publicly (they're like passwords)
- Regenerate tokens unnecessarily (breaks old links)
- Assign developers without reviewing their profiles first
- Delete CustomerDeveloperAssignment records (historical data)

## Related Documentation

- [Customer Portal Setup](./CUSTOMER_PORTAL_SETUP.md) - Technical implementation details
- [Learning Resources](./LEARNING_RESOURCES.md) - Developer training materials
- [Assessment System](./RESOURCES_SETUP.md) - How assessments work

---

**Quick Start Checklist**

- [ ] Create customer in admin
- [ ] Assign 1+ developers (inline form)
- [ ] Save customer (auto-generates token)
- [ ] Copy shareable URL from "Shareable Access"
- [ ] Send URL to customer via email
- [ ] Customer reviews developers (no login)
- [ ] Customer approves/rejects each developer
- [ ] Customer signs contract (if applicable)
- [ ] Check admin for updated approval status
- [ ] View customer notes on each developer

**Status**: ✅ Live in Admin Dashboard
**Last Updated**: December 16, 2025
