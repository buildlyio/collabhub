# Smoke Testing for CollabHub

## Overview
This test suite provides low-maintenance regression testing that catches critical errors before deployment.

## What It Tests

### 1. **Page Load Tests**
- All public pages (/, /login/, /register/)
- Authenticated user pages (/dashboard/, profile edit)
- Admin pages (developer list, customer list, quizzes, resources)
- Customer dashboard pages
- **Catches:** 500 errors, FieldErrors, template syntax errors

### 2. **Form Rendering Tests**
- Registration, login, profile edit forms
- Admin forms (quiz creation, resource creation)
- **Catches:** Form initialization errors, missing context variables

### 3. **Template Regression Tests**
- Checks for deprecated method calls (like `get_team_member_type_display`)
- Verifies TeamMember types display correctly
- Tests customer-facing pages for common errors
- **Catches:** FieldErrors from database schema changes

### 4. **API Smoke Tests**
- Team members API
- Customers API
- Forge marketplace API
- **Catches:** Serializer errors, API endpoint failures

### 5. **Database Integrity Tests**
- TeamMember types ManyToMany relationship
- Model __str__ methods
- Basic queries on all major models
- **Catches:** Migration issues, relationship errors

## Running Tests

### Manual Execution
```bash
# Run all smoke tests
python manage.py test onboarding.test_smoke --settings=mysite.settings.dev

# Run specific test class
python manage.py test onboarding.test_smoke.PageLoadSmokeTests --settings=mysite.settings.dev

# Run with more detail
python manage.py test onboarding.test_smoke --settings=mysite.settings.dev -v 2

# Keep test database for faster reruns
python manage.py test onboarding.test_smoke --settings=mysite.settings.dev --keepdb
```

### Automatic Pre-Push Hook
The pre-push hook automatically runs smoke tests before every `git push`:

```bash
# Normal push - tests run automatically
git push origin main

# Skip tests if absolutely necessary (not recommended)
git push origin main --no-verify
```

**Hook is installed at:** `.git/hooks/pre-push`

## Maintenance Philosophy

These tests are designed to be **low maintenance**:

1. **No Specific IDs/Content**: Tests don't check for specific text or IDs that change frequently
2. **Status Code Based**: Primarily checks that pages return 200/302/404, not 500
3. **Generic Assertions**: Looks for presence of forms, not specific fields
4. **Auto-Discovery**: Could be extended to auto-discover URLs from Django's URL patterns
5. **Flexible Checks**: Uses `assertIn(status, [200, 302, 404])` to handle redirects gracefully

## When Tests Fail

If smoke tests fail:

1. **Read the error message** - it will tell you which page/test failed
2. **Check recent changes** - did you modify models, views, or templates?
3. **Run the specific test** for more detail:
   ```bash
   python manage.py test onboarding.test_smoke.PageLoadSmokeTests.test_admin_pages_load --settings=mysite.settings.dev -v 2
   ```
4. **Fix the issue** - these tests catch real bugs that would affect production
5. **Re-run tests** to verify the fix

## Common Issues Caught

- ✅ FieldErrors from database schema changes (like `get_team_member_type_display()`)
- ✅ Missing context variables in templates
- ✅ Broken imports or circular dependencies
- ✅ Form initialization errors
- ✅ API serializer failures
- ✅ Template syntax errors
- ✅ Missing migrations

## Extending Tests

To add new page tests, just add URLs to the appropriate list:

```python
def test_new_feature_pages(self):
    """Test new feature pages load"""
    self.client.login(username='admin_test', password='testpass123')
    
    new_urls = [
        '/new/feature/page/',
        '/another/new/page/',
    ]
    
    for url in new_urls:
        response = self.client.get(url, follow=True)
        self.assertIn(response.status_code, [200, 302, 404])
```

## Performance

- **First run:** ~10-30 seconds (creates test database)
- **Subsequent runs:** ~3-10 seconds (with `--keepdb`)
- **Pre-push overhead:** Minimal, catches issues before they reach production

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/tests.yml
- name: Run Smoke Tests
  run: |
    python manage.py test onboarding.test_smoke --settings=mysite.settings.production --keepdb
```

## Benefits

1. **Prevents Regressions**: Catches breaking changes before they're pushed
2. **Fast Feedback**: Runs in seconds, not minutes
3. **Low Maintenance**: No need to update tests when adding features
4. **Safety Net**: Confidence that basic functionality works
5. **Documentation**: Serves as a map of all major pages/features
