# Production Deployment Guide

## Current Status (as of 2025-12-17 18:45 UTC)

### Issues Resolved ✅
- All code fixes have been deployed
- Migrations 0008-0016 have been applied in production
- Static files have been collected

### Outstanding Issues ⚠️

#### 1. FieldError on Customer Developer Detail Page (PRODUCTION BUG)
- **URL**: https://collab.buildly.io/onboarding/client/shared/[token]/developer/[id]/
- **Status**: Code is fixed, but ~~Python process not restarted~~ issue persists
- **Root Cause**: Old Python bytecode (.pyc files) still in memory
- **Evidence**: 
  - Smoke tests pass locally ✅
  - Code is correct ✅
  - Migration 0016 applied successfully ✅
  - But production still throws FieldError
- **Solution**: 
  1. Force app container restart in DigitalOcean App Platform
  2. Clear Python cache and restart gunicorn workers
  3. Or: Run `find . -type d -name __pycache__ -exec rm -r {} +` before restart

#### 2. GitHub Issue Submission Failing (404 Error)
- **Status**: Configuration missing
- **Error**: `Failed to create GitHub issue: 404 - {"message":"Not Found"...}`
- **Root Cause**: GITHUB_ERROR_TOKEN environment variable not set in DigitalOcean
- **Required Vars to Add**:
  ```
  GITHUB_ERROR_REPO=greglind/collabhub
  GITHUB_ERROR_TOKEN=[your-github-token]
  ```
- **Solution**: 
  1. Generate new GitHub personal access token: https://github.com/settings/tokens
  2. Select scopes: `repo` (full control of private repositories)
  3. Add to DigitalOcean App Platform environment variables
  4. Restart the app


## Deployment Steps

### IMMEDIATE ACTION REQUIRED - Fix Production 404 Error

To fix the FieldError that's still appearing in production:

**Option 1: Force Container Restart (Recommended)**
```bash
# In DigitalOcean App Platform console:
1. Go to Components → squid-app → Restart
2. This will clear Python bytecode and restart the process
3. Test: https://collab.buildly.io/onboarding/client/shared/[token]/developer/[id]/
```

**Option 2: Manual Cache Clear (if restart unavailable)**
```bash
doctl apps exec [app-id] --command "find . -type d -name __pycache__ -delete && find . -name '*.pyc' -delete"
doctl apps exec [app-id] --restart
```

### Setup GitHub Error Reporting

1. Go to: https://github.com/settings/tokens/new
2. Create token with name: `CollabHub Error Reporter`
3. Select scope: `repo` (full control)
4. Copy the token
5. In DigitalOcean App Platform:
   - Go to Settings → Environment
   - Add: `GITHUB_ERROR_TOKEN=[token-you-just-created]`
   - Add: `GITHUB_ERROR_REPO=greglind/collabhub`
   - Deploy

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
