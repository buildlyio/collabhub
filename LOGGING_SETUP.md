# Comprehensive Logging Setup for Production Debugging

## Overview
Detailed logging has been implemented to capture and display the exact errors occurring on the customer developer detail page. All logs now output to stdout/stderr which DigitalOcean captures in its runtime logs.

## What Was Changed

### 1. Enhanced Error Middleware (`onboarding/error_middleware.py`)
- **Added**: `logging.getLogger('collabhub.errors')`
- **Captures**: All exceptions with full stack traces
- **Output**: Sends error details to stderr with visual formatting (=== separators)
- **Shows**:
  - Error type (e.g., FieldError, DoesNotExist, etc.)
  - Error message
  - Request path and method
  - User information
  - Timestamp
  - Full Python traceback

**Example Output:**
```
================================================================================
❌ EXCEPTION CAUGHT IN MIDDLEWARE
================================================================================
Error Type: FieldError
Error Message: Cannot resolve keyword 'types' into field...
Path: /onboarding/client/shared/[token]/developer/20/
Method: GET
User: Customer [customer_id]
Timestamp: 2025-01-15T10:45:32.123456

Full Traceback:
  File "onboarding/views.py", line 1245, in customer_shared_developer_detail
    ...
```

### 2. Detailed View Logging (`onboarding/views.py` - customer_shared_developer_detail)
- **Added**: Step-by-step logging through the entire view execution
- **Logs**: Each major operation with checkmarks (✓) or errors (❌)
- **Steps logged**:
  1. Customer lookup by token
  2. Developer lookup
  3. Assignment verification
  4. Quiz answers query
  5. Assessment score calculation
  6. Resources query
  7. Template render
  
**Example Output:**
```
🔍 customer_shared_developer_detail called - token=abc123, developer_id=20
Step 1: Looking up customer with token=abc123
✓ Found customer: 42 - Acme Corp
Step 2: Looking up developer with id=20
✓ Found developer: 20 - John Smith
Step 3: Verifying assignment - customer=42, developer=20
✓ Assignment verified
Step 4: Querying quiz answers for developer=20
✓ Found 45 quiz answers
Step 5: Calculating assessment scores
✓ Assessment scores - MC: 85.0%, Essay: 90.0%, Overall: 87.5%
Step 6: Getting developer resources
✓ Found 3 resources
Step 7: Building context for template render
✓ Context prepared, about to render template
✅ Successfully rendered customer_shared_developer_detail page
```

If any step fails, it logs the error with full traceback:
```
❌ Error in customer_shared_developer_detail: Cannot resolve keyword 'types'...
[Full Python traceback]
```

### 3. Django Logging Configuration

#### Production (`mysite/settings/production.py`)
- Loggers output to **console/stdout** at **DEBUG level**
- Captures:
  - `django`: Django framework messages (INFO level)
  - `django.request`: HTTP request/response (INFO level)
  - `collabhub`: App-level logs (DEBUG level)
  - `collabhub.errors`: Exception handling (DEBUG level)
  - `collabhub.views`: View execution (DEBUG level)

#### Development (`mysite/settings/base.py`)
- Same structure as production for consistency
- Allows testing logging locally

## How to Read the Logs

### In DigitalOcean Dashboard

1. Go to your App Platform app
2. Click on the component (e.g., "web")
3. Look at the **Runtime Logs** tab
4. Search for:
   - `❌` (error indicator)
   - `EXCEPTION CAUGHT IN MIDDLEWARE` (detailed errors)
   - `customer_shared_developer_detail` (view execution)
   - `FieldError` or other error types

### Log Levels Explained
- **DEBUG**: Detailed diagnostic info (steps 1-7 logs)
- **INFO**: Confirmations and milestones (✓ Found messages)
- **ERROR**: Problems that occurred (❌ messages)
- **CRITICAL**: System-level failures

## Example Error Diagnosis Workflow

### Scenario: FieldError on developer detail page

**Look for in logs:**
```
❌ EXCEPTION CAUGHT IN MIDDLEWARE
Error Type: FieldError
Error Message: Cannot resolve keyword 'types' into field...
Path: /onboarding/client/shared/[token]/developer/20/

Full Traceback:
  File "onboarding/templates/customer_shared_developer_detail.html", line 15, in <module>
    {% for type in developer.types.all %}
  File "django/db/models/fields/related_descriptors.py", ...
    raise FieldError(...)
```

**Tells you:**
- Error is a `FieldError`
- Occurs in the template at line 15
- Trying to access `developer.types` field
- Solution: Check if `types` is a valid property/method on TeamMember model

### Scenario: Assignment not found

**Look for in logs:**
```
Step 3: Verifying assignment - customer=42, developer=20
❌ Error getting assignment for customer=42, developer=20: ...
Failed to find matching CustomerDeveloperAssignment
```

**Tells you:**
- Assignment lookup failed
- Either customer or developer IDs are wrong
- Or the assignment doesn't exist in the database

## Deployment Instructions

1. **Code is already pushed**: Latest commit includes all logging
2. **Deploy normally**: No additional environment variables needed
3. **Watch logs immediately after deploy**:
   - Logging will capture errors as they happen
   - Errors will show with full context
4. **Check DigitalOcean runtime logs** after customer hits the detail page

## Testing Locally

```bash
# The logging will work in both dev and production settings
python manage.py runserver --settings=mysite.settings.dev
# or
python manage.py runserver --settings=mysite.settings.production
```

When you access the customer developer detail page, you'll see the step-by-step logs in your terminal console.

## Disabling Logging

If needed, comment out the logger calls in the view (currently 7 logger statements), or adjust log levels in `mysite/settings/production.py`.

## Next Steps

1. **Deploy this version** to production
2. **Have customer access** the developer detail page
3. **Check DigitalOcean logs** for the error details
4. **Share the relevant log snippet** to identify the exact issue
5. **Fix** based on the error details now visible in logs

---

**Status**: ✅ Logging implementation complete and ready for deployment
**Files Modified**: 
- `onboarding/error_middleware.py`
- `onboarding/views.py`
- `mysite/settings/production.py`
- `mysite/settings/base.py`

**Commit**: `13ea23d`
