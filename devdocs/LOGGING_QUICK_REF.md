# Quick Logging Reference

## When Error Occurs

You'll now see in DigitalOcean logs:

```
🔍 customer_shared_developer_detail called - token=..., developer_id=...
Step 1: Looking up customer...
✓ Found customer: ...
Step 2: Looking up developer...
[ERROR occurs here or later]
❌ EXCEPTION CAUGHT IN MIDDLEWARE
================================================================================
Error Type: [ACTUAL ERROR TYPE]
Error Message: [ACTUAL ERROR MESSAGE]
Path: /onboarding/client/shared/.../developer/20/
Full Traceback:
  [Python stack trace showing exactly where error occurred]
================================================================================
```

## Key Things to Look For

### Error Not Showing? Look for:
- Search: `EXCEPTION CAUGHT IN MIDDLEWARE` 
- Search: `collabhub` for app logs
- Check both **Runtime Logs** tab (not just Deploy)

### Which Step Failed?
- `Step 1:` → Customer lookup failed → Token invalid/expired
- `Step 2:` → Developer lookup failed → Developer ID invalid
- `Step 3:` → Assignment verification failed → No access to developer
- `Step 4:` → Quiz query failed → Database issue
- `Step 5:` → Score calculation failed → Data integrity issue
- `Step 6:` → Resources query failed → Database issue
- `Step 7:` → Template render failed → Template/context issue

### FieldError?
Shows up as:
```
Error Type: FieldError
Error Message: Cannot resolve keyword 'types' into field...
```
Usually means: Model field doesn't exist or was removed

### Template Rendering Error?
Shows up as:
```
Error Type: TemplateDoesNotExist
Error Message: customer_shared_developer_detail.html
```
Or:
```
Error Type: FieldError
...in customer_shared_developer_detail.html line 15...
```

## What Each Symbol Means

| Symbol | Meaning |
|--------|---------|
| 🔍 | View function called |
| ✓ | Step completed successfully |
| ❌ | Error encountered |
| ✅ | Entire page rendered successfully |
| Step 1-7 | Progress through view execution |

## Production Deployment Checklist

- [ ] Latest code deployed (`commit 27d5831`)
- [ ] Check DigitalOcean Runtime Logs for your app
- [ ] Customer accesses the developer detail page
- [ ] Look for `customer_shared_developer_detail` in logs
- [ ] Either see `✅ Successfully rendered` (working) or `❌ EXCEPTION` (error)
- [ ] If error, identify the step and error type
- [ ] Share error details to fix

## Common Next Steps

If you see:
- **Step 1 error**: Token is invalid or expired, check customer is active
- **Step 2 error**: Developer ID doesn't exist, check URL parameter
- **Step 3 error**: Customer has no assignment, check CustomerDeveloperAssignment table
- **Step 7 error**: Template issue, check template file exists and syntax is correct
- **FieldError on types**: Model property doesn't exist, check TeamMember.types definition

---

**No more blind debugging!** The error will be clearly visible in the logs now.
