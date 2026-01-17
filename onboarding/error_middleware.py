"""
Middleware for handling errors and submitting them to GitHub Issues
"""
import traceback
import sys
import logging
from django.shortcuts import render
from django.conf import settings
import requests
from datetime import datetime

# Set up logging
logger = logging.getLogger('collabhub.errors')


class ErrorHandlerMiddleware:
    """
    Custom middleware to catch all exceptions, display user-friendly error pages,
    and automatically create GitHub issues for tracking.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions and create GitHub issues"""
        # In development, let Django show the full traceback
        if settings.DEBUG:
            return None
        
        # Get exception details
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Create error context for template
        error_context = {
            'error_type': exc_type.__name__ if exc_type else 'Unknown Error',
            'error_message': str(exc_value),
            'path': request.path,
            'method': request.method,
            'user': request.user if hasattr(request, 'user') else None,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Log the full error with traceback
        log_message = f"\n{'='*80}\n❌ EXCEPTION CAUGHT IN MIDDLEWARE\n{'='*80}\nError Type: {error_context['error_type']}\nError Message: {error_context['error_message']}\nPath: {error_context['path']}\nMethod: {error_context['method']}\nUser: {error_context['user']}\nTimestamp: {error_context['timestamp']}\n\nFull Traceback:\n{error_traceback}\n{'='*80}\n"
        
        # Print to console (will show in DigitalOcean logs)
        print(log_message, file=sys.stderr)
        logger.error(log_message, exc_info=True)
        
        # Submit to GitHub if configured (DEBUG already handled above)
        if (
            hasattr(settings, 'GITHUB_ERROR_REPO') and 
            hasattr(settings, 'GITHUB_ERROR_TOKEN') and
            settings.GITHUB_ERROR_TOKEN):  # Only if token is actually set
            try:
                self.create_github_issue(error_context, error_traceback)
            except Exception as e:
                # Don't let GitHub submission failures crash the error handler
                error_msg = f"❌ Failed to create GitHub issue: {e}"
                print(error_msg, file=sys.stderr)
                logger.error(error_msg, exc_info=True)
        elif not settings.DEBUG and not getattr(settings, 'GITHUB_ERROR_TOKEN', None):
            logger.info("ℹ️ GitHub error reporting not configured (GITHUB_ERROR_TOKEN not set)")
        
        # Return user-friendly error page
        return render(request, '500.html', error_context, status=500)
    
    def create_github_issue(self, error_context, traceback_text):
        """
        Create a GitHub issue for the error, or comment on existing issue if duplicate
        
        Requires these settings:
        - GITHUB_ERROR_REPO: Repository in format "owner/repo"
        - GITHUB_ERROR_TOKEN: GitHub personal access token with repo access
        """
        repo = settings.GITHUB_ERROR_REPO
        token = settings.GITHUB_ERROR_TOKEN
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        
        # Build issue title (used for searching)
        title = f"🐛 {error_context['error_type']}: {error_context['error_message'][:80]}"
        
        # Search for existing open issues with same error
        search_query = f"is:issue is:open repo:{repo} {error_context['error_type']} in:title"
        search_url = f"https://api.github.com/search/issues"
        search_params = {'q': search_query}
        
        search_response = requests.get(search_url, headers=headers, params=search_params)
        
        existing_issue = None
        if search_response.status_code == 200:
            issues = search_response.json().get('items', [])
            # Look for exact match on error message
            for issue in issues:
                if error_context['error_message'][:80] in issue['title']:
                    existing_issue = issue
                    break
        
        occurrence_info = f"""
### Occurrence Details
**URL:** `{error_context['path']}`
**Method:** `{error_context['method']}`
**User:** {error_context['user'].username if error_context['user'] and error_context['user'].is_authenticated else 'Anonymous'}
**Timestamp:** {error_context['timestamp']}
"""
        
        if existing_issue:
            # Add comment to existing issue
            comment_body = f"""## Error Occurred Again

{occurrence_info}

<details>
<summary>Traceback</summary>

```python
{traceback_text}
```
</details>
"""
            comment_url = existing_issue['comments_url']
            comment_response = requests.post(comment_url, json={'body': comment_body}, headers=headers)
            
            if comment_response.status_code == 201:
                print(f"✓ Added comment to existing GitHub issue: {existing_issue['html_url']}")
            else:
                print(f"❌ Failed to comment on issue: {comment_response.status_code}")
        else:
            # Create new issue
            body = f"""## Error Details
        
**Error Type:** `{error_context['error_type']}`
**Error Message:** {error_context['error_message']}

{occurrence_info}

## Traceback

```python
{traceback_text}
```

---
*This issue was automatically created by the error handler middleware.*
"""
            
            create_url = f"https://api.github.com/repos/{repo}/issues"
            data = {
                'title': title,
                'body': body,
                'labels': ['bug', 'auto-generated', 'production-error'],
            }
            
            response = requests.post(create_url, json=data, headers=headers)
            
            if response.status_code == 201:
                issue_url = response.json().get('html_url')
                print(f"✓ GitHub issue created: {issue_url}")
            else:
                print(f"❌ Failed to create GitHub issue: {response.status_code} - {response.text}")
