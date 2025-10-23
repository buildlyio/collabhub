# Forge Marketplace Module

The Forge module provides a complete marketplace system for Buildly-compatible applications. It includes repository validation, Stripe payment processing, and comprehensive API endpoints for browsing and purchasing apps.

## Features

- **Repository Validation**: GitHub integration with BUILDLY.yaml parsing and file existence checks
- **Payment Processing**: Stripe integration with Labs customer discounts (50% off)
- **API Endpoints**: Public browsing, authenticated purchases, admin management
- **Admin Interface**: Rich Django admin for managing apps, purchases, and validations
- **Management Commands**: Import repositories, validate apps, create test data

## Quick Start

### 1. Import Buildly Marketplace Repositories

```bash
# Set your GitHub API token
export GITHUB_API_TOKEN=your_github_token_here

# Run the import script
./scripts/import_marketplace.sh
```

This will:
- Import all repositories from `buildly-marketplace` GitHub organization
- Create Forge apps priced at $49 each
- Mark them as Docker deployable
- Run validation on each repository

### 2. Manual Import Command

```bash
# Import with custom options
python manage.py import_marketplace_repos \
    --price-cents 4900 \
    --skip-existing \
    --validate \
    --limit 10

# Dry run to see what would be imported
python manage.py import_marketplace_repos --dry-run
```

### 3. Validate Repositories

```bash
# Validate all published apps
python manage.py validate_forge_repos --published-only

# Validate specific app
python manage.py validate_forge_repos --slug my-app

# Force validation even if recently validated
python manage.py validate_forge_repos --force
```

### 4. Create Test Data

```bash
# Create test users and sample purchases
python manage.py create_forge_test_data --users 5 --apps 10

# Clear existing test data first
python manage.py create_forge_test_data --clear --users 3
```

## API Endpoints

### Public API (No Authentication)

```
GET /forge/api/apps/
- List published apps with filtering
- Query params: categories, targets, search

GET /forge/api/apps/{slug}/
- Get detailed app information
```

### Authenticated API

```
GET /forge/api/purchases/
- User's purchase history

POST /forge/api/purchases/create_checkout/
- Create Stripe checkout session
- Body: {"forge_app_id": "uuid"}

GET /forge/api/entitlements/
- User's owned apps
```

### Admin API (Staff Only)

```
GET/POST /forge/admin-api/apps/
- Full CRUD operations on apps

POST /forge/admin-api/apps/{slug}/validate/
- Trigger repository validation

GET /forge/admin-api/purchases/
- View all purchases with filtering

GET /forge/admin-api/entitlements/
- View all entitlements
```

### Webhooks

```
POST /forge/webhook/stripe/
- Stripe payment webhook handler
```

## Configuration

### Environment Variables

```bash
# Required for repository import and validation
GITHUB_API_TOKEN=your_github_token

# Required for Stripe payments
STRIPE_API_KEY=sk_live_or_test_key
STRIPE_WEBHOOK_SECRET=whsec_webhook_secret

# Optional - Frontend URL for payment redirects
FRONTEND_URL=https://yourdomain.com
```

### Django Settings

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'forge',
    'rest_framework',
]
```

Include URLs:

```python
urlpatterns = [
    # ... other patterns
    path('forge/', include('forge.urls')),
]
```

## Models

### ForgeApp
- Core marketplace application with pricing, categories, validation
- Links to GitHub repository with owner/name tracking
- Supports multiple deployment targets (docker, k8s, github-pages, etc.)

### RepoValidation
- Repository validation results with missing items tracking
- GitHub commit SHA validation
- Target-specific validation rules

### Purchase
- Stripe payment transactions with Labs customer discounts
- Status tracking (pending, completed, failed)
- Links to Stripe payment intents

### Entitlement
- User ownership of apps after successful purchase
- Automatic creation after payment completion

### UserProfile
- Extended user data for Labs customer status
- Determines discount eligibility

## Repository Validation

The validation service checks for:

1. **Required Files**: README.md, BUILDLY.yaml, Dockerfile
2. **BUILDLY.yaml Structure**: Service definitions, port configurations
3. **Target-Specific Requirements**:
   - Docker: Dockerfile, docker-compose.yml
   - Kubernetes: k8s/ directory with manifests
   - GitHub Pages: _config.yml, index.html

## Payment Flow

1. User browses apps via public API
2. User initiates purchase via `create_checkout` endpoint
3. Stripe checkout session created with metadata
4. User completes payment on Stripe
5. Stripe webhook processes payment completion
6. Entitlement created automatically

## Admin Interface

Access at `/admin/forge/` with staff account:

- **Forge Apps**: Manage apps, trigger validation, bulk actions
- **Purchases**: View payment history, status management
- **Entitlements**: User ownership tracking
- **Repo Validations**: Validation results and history

## Development

### Running Tests

```bash
# Run Forge module tests
python manage.py test forge

# Test with coverage
python manage.py test forge --coverage
```

### API Testing

```bash
# List apps
curl http://localhost:8000/forge/api/apps/

# Get app details
curl http://localhost:8000/forge/api/apps/buildly-dashboard/

# Create checkout (authenticated)
curl -X POST http://localhost:8000/forge/api/purchases/create_checkout/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{"forge_app_id": "uuid"}'
```

## Troubleshooting

### Common Issues

1. **GitHub API Rate Limits**
   - Use authenticated requests with GITHUB_API_TOKEN
   - Import script handles rate limiting automatically

2. **Stripe Webhook Verification**
   - Ensure STRIPE_WEBHOOK_SECRET is correct
   - Check webhook endpoint configuration in Stripe dashboard

3. **Repository Validation Failures**
   - Check repository permissions and existence
   - Verify BUILDLY.yaml format and required files

### Logs

Monitor Django logs for detailed error information:

```bash
tail -f logs/django.log | grep forge
```

## License

This module is part of the CollabHub project and follows the same license terms.