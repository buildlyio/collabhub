# Production Deployment Guide

## Current Status (as of 2025-12-17)

### Recent Fixes Committed:
1. ✅ Fixed all FieldError issues from `get_team_member_type_display()` method
   - Replaced with iteration through `types.all()` ManyToMany field
   - Added `@property types` to TeamMember model as backward compatibility alias
   - Updated 10+ templates

2. ✅ Fixed STATIC_URL for Forge marketplace logo
   - Updated forge/models.py to use Django STATIC_URL
   - Updated marketplace templates to use STATIC_URL template tag

3. ✅ Added error handling to TeamMember model methods
   - `types` property has fallback handling
   - `__str__()` and `get_profile_types_display()` have error handling

4. ✅ Created comprehensive smoke test suite
   - 15 tests covering pages, forms, templates, APIs, and database integrity
   - Pre-push git hook to run tests before deployment
   - Tests included in codebase

## Known Issues in Production

### 1. FieldError on Customer Developer Detail Page
- **URL**: https://collab.buildly.io/onboarding/client/shared/[token]/developer/[id]/
- **Status**: Fixed in code commit `d39b908`
- **Root Cause**: Production has old code without the `types` property fixes
- **Solution**: Deploy latest code from main branch

### 2. Forge Logo Not Displaying
- **URL**: Marketplace and app detail pages
- **Status**: Fixed in code commit `d39b908`
- **Root Cause**: Using `/static/` hardcoded paths instead of STATIC_URL
- **Solution**: Deploy latest code and run `python manage.py collectstatic`

### 3. MailerSend Environment Variables Missing
- **Status**: Not configured in DigitalOcean App Platform
- **Required Vars**:
  ```
  EMAIL_HOST=smtp.mailersend.net
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  DEFAULT_FROM_EMAIL=admin@buildly.io
  MAILERSEND_SMTP_USERNAME=MS_Yh4iLk@buildly.io
  MAILERSEND_SMTP_PASSWORD=mssp.xdkL53K.3vz9dleke7qlkj50.YtSrOOd
  EMAIL_SUBJECT_PREFIX=[Buildly Labs]
  ```
- **Solution**: Add these to DigitalOcean App Platform environment variables

### 4. GitHub Error Token Invalid
- **Status**: Getting 401 errors when creating issues
- **Solution**: Generate new GitHub personal access token with `repo` scope

## Deployment Steps

### Step 1: Deploy Code
```bash
git push origin main
# Wait for DigitalOcean App Platform to auto-deploy
```

### Step 2: Run Migrations
```bash
# DigitalOcean will run migrations automatically on deploy
# If manual needed:
doctl apps exec [app-id] -- python manage.py migrate --settings=mysite.settings.production
```

### Step 3: Collect Static Files
```bash
# DigitalOcean runs this automatically
# If manual needed:
doctl apps exec [app-id] -- python manage.py collectstatic --noinput --settings=mysite.settings.production
```

### Step 4: Add Environment Variables to DigitalOcean
1. Go to DigitalOcean App Platform console
2. Select your app (squid-app-sejn2)
3. Click "Settings"
4. Add the MailerSend variables listed above
5. Deploy

### Step 5: Verify Fixes
After deployment, test:
1. Customer developer detail page: https://collab.buildly.io/onboarding/client/shared/[token]/developer/[id]/
2. Forge marketplace: Check logo displays on app cards
3. Email notifications: Create a test user signup and verify admin@buildly.io receives email
4. GitHub issues: Trigger an error and verify it's reported

## Testing Locally

### Run Smoke Tests
```bash
python manage.py test onboarding.test_smoke --settings=mysite.settings.dev --keepdb
```

### Test Specific Page
```bash
python manage.py shell --settings=mysite.settings.dev
>>> from onboarding.models import TeamMember
>>> tm = TeamMember.objects.first()
>>> tm.types.all()  # Should return QuerySet
>>> print(tm)  # Should print with types
```

## Key Files Modified in Latest Commits

### commit d39b908
- `forge/models.py` - Updated logo_url_or_default property
- `forge/templates/forge/marketplace.html` - Updated STATIC_URL references
- `onboarding/models.py` - Added error handling to types property

### commit ee0262d
- `onboarding/models.py` - Fixed TeamMember.__str__() and methods
- `onboarding/signals.py` - Updated email notification to use type.label
- 10+ templates - Fixed types iteration

## Checklist for Production Verification

After deployment:
- [ ] Customer shared developer detail pages load without FieldError
- [ ] Forge marketplace displays logos correctly
- [ ] Email notifications are received for new signups
- [ ] GitHub issues are created for errors
- [ ] Admin dashboard loads without errors
- [ ] All admin pages load without errors
- [ ] Smoke tests pass: `python manage.py test onboarding.test_smoke --settings=mysite.settings.production`

## Rollback Plan

If issues occur after deployment:
```bash
git revert d39b908  # Revert latest commit
git push origin main
# Wait for auto-deploy
```

Or revert to previous stable commit if needed.
