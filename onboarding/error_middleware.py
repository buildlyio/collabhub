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
        
        # Submit to GitHub if configured and not in DEBUG mode
        if not settings.DEBUG and hasattr(settings, 'GITHUB_ERROR_REPO') and hasattr(settings, 'GITHUB_ERROR_TOKEN'):
            try:
                self.create_github_issue(error_context, error_traceback)
            except Exception as e:
                # Don't let GitHub submission failures crash the error handler
                error_msg = f"❌ Failed to create GitHub issue: {e}"
                print(error_msg, file=sys.stderr)
                logger.error(error_msg, exc_info=True)
        
        # Return user-friendly error page
        return render(request, '500.html', error_context, status=500)
    
    def create_github_issue(self, error_context, traceback_text):
        """
        Create a GitHub issue for the error
        
        Requires these settings:
        - GITHUB_ERROR_REPO: Repository in format "owner/repo"
        - GITHUB_ERROR_TOKEN: GitHub personal access token with repo access
        """
        repo = settings.GITHUB_ERROR_REPO
        token = settings.GITHUB_ERROR_TOKEN
        
        # Build issue title and body
        title = f"🐛 {error_context['error_type']}: {error_context['error_message'][:80]}"
        
        body = f"""## Error Details
        
**Error Type:** `{error_context['error_type']}`
**Error Message:** {error_context['error_message']}

**URL:** `{error_context['path']}`
**Method:** `{error_context['method']}`
**User:** {error_context['user'].username if error_context['user'] and error_context['user'].is_authenticated else 'Anonymous'}
**Timestamp:** {error_context['timestamp']}

## Traceback

```python
{traceback_text}
```

---
*This issue was automatically created by the error handler middleware.*
"""
        
        # Create the issue
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        
        data = {
            'title': title,
            'body': body,
            'labels': ['bug', 'auto-generated', 'production-error'],
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            issue_url = response.json().get('html_url')
            print(f"GitHub issue created: {issue_url}")
        else:
            print(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
