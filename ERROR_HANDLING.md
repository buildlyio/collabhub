# Error Handling & GitHub Issue Tracking Setup

## Overview

The application now includes automatic error handling that:
1. **Disables DEBUG mode in production** - Shows user-friendly error pages instead of stack traces
2. **Catches all unhandled exceptions** - Prevents application crashes
3. **Creates GitHub Issues automatically** - All production errors are tracked
4. **Provides user-friendly recovery** - Clear navigation back to the application

## Production Settings

### DEBUG Mode
- **Development**: `DEBUG = True` (shows detailed error pages)
- **Production**: `DEBUG = False` (shows custom 500.html page)

### Current Status
✅ Production now has `DEBUG = False` in `mysite/settings/production.py`

## GitHub Error Reporting

### Configuration

Errors are automatically submitted to this repository (`greglind/collabhub`) as GitHub issues.

You only need to add this environment variable to your production environment:

```bash
# GitHub Personal Access Token with 'repo' scope
GITHUB_ERROR_TOKEN=your_github_token_here
```

Note: Error issues will appear in the Issues tab of this repository with the `production-error` label.

### Creating a GitHub Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "CollabHub Error Reporting"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
     - ✅ `repo:status`
     - ✅ `repo_deployment`
     - ✅ `public_repo`
5. Click "Generate token"
6. Copy the token immediately (you won't see it again!)
7. Add to your production environment variables as `GITHUB_ERROR_TOKEN`

### What Gets Reported

When an error occurs in production, a GitHub issue is automatically created with:

- **Error Type**: The exception class name
- **Error Message**: The exception message
- **URL Path**: Where the error occurred
- **HTTP Method**: GET, POST, etc.
- **User**: Username or "Anonymous"
- **Timestamp**: When the error occurred
- **Full Traceback**: Complete Python stack trace
- **Labels**: `bug`, `auto-generated`, `production-error`

### Example Issue

```markdown
🐛 NameError: name 'timezone_now' is not defined

## Error Details

**Error Type:** `NameError`
**Error Message:** name 'timezone_now' is not defined

**URL:** `/onboarding/client/shared/.../approve/`
**Method:** `POST`
**User:** john_doe
**Timestamp:** 2025-12-17T16:36:18

## Traceback

\`\`\`python
Traceback (most recent call last):
  File "/app/onboarding/views.py", line 1257
    assignment.reviewed_at = timezone_now()
NameError: name 'timezone_now' is not defined
\`\`\`
```

## Error Pages

### 500 - Internal Server Error

Located at: `mysite/templates/500.html`

Features:
- ✅ Animated error icon
- ✅ Clear error message
- ✅ Error type badge (if available)
- ✅ "Go to Homepage" button
- ✅ "Go Back" button
- ✅ Quick navigation links to common pages
- ✅ Support email contact
- ✅ Auto-prompt after 30 seconds of inactivity
- ✅ Timestamp of error

### 404 - Page Not Found

Located at: `mysite/templates/404.html`

For pages that don't exist (already configured).

## Middleware

The error handling is implemented in:
- **File**: `onboarding/error_middleware.py`
- **Class**: `ErrorHandlerMiddleware`
- **Registered in**: `mysite/settings/base.py` MIDDLEWARE list

### How It Works

1. User triggers an error in the application
2. Middleware catches the exception
3. If in production (`DEBUG = False`) and GitHub credentials are configured:
   - Creates a detailed GitHub issue with full context
   - Labels it appropriately for triage
4. Displays user-friendly 500.html page with:
   - Error type (safe to show)
   - Navigation options
   - Quick links to common pages
5. Logs error details to console as backup

## Testing

### Test in Development

```python
# Add a test view to trigger an error
def test_error(request):
    raise ValueError("This is a test error")
```

### Test GitHub Integration

1. Set `DEBUG = False` in dev.py temporarily
2. Add `GITHUB_ERROR_REPO` and `GITHUB_ERROR_TOKEN` to your environment
3. Trigger an error
4. Check your GitHub repo for the new issue
5. Set `DEBUG = True` again after testing

## Deployment Checklist

- [x] Set `DEBUG = False` in production.py ✅ (DONE)
- [x] Configure `GITHUB_ERROR_REPO` to greglind/collabhub ✅ (DONE)
- [ ] Add `GITHUB_ERROR_TOKEN` environment variable (REQUIRED)
- [ ] Test error page displays correctly
- [ ] Verify GitHub issue creation works
- [x] Update `ALLOWED_HOSTS` with production domains ✅ (DONE)
- [ ] Configure logging for persistent error storage
- [ ] Set up email notifications for critical errors (optional)

## Security Notes

⚠️ **Important**: The error page only shows:
- Error type (e.g., "ValueError", "NameError")
- Generic error message
- Timestamp

It does NOT show:
- ❌ Full stack traces (only in GitHub issues)
- ❌ Sensitive data or credentials
- ❌ Database queries
- ❌ Internal paths (sanitized in GitHub issues)

## Monitoring

### GitHub Issue Dashboard

All production errors appear as issues in your GitHub repo:
- Filter by label: `production-error`
- Sort by newest first
- Close issues when resolved
- Comment with fixes and deployment notes

### Future Enhancements

Consider adding:
- [ ] Sentry or Rollbar integration for real-time monitoring
- [ ] Email notifications to admin team
- [ ] Slack webhook for critical errors
- [ ] Error rate limiting (prevent spam from repeated errors)
- [ ] Error deduplication (group similar errors)
- [ ] Weekly error summary reports

## Support

For questions or issues with error handling:
- Email: support@buildly.io
- GitHub: Create an issue in the repo
