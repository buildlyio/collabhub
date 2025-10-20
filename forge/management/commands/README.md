# Forge Marketplace - GitHub Apps Loader

This directory contains management commands for loading apps from GitHub repositories into The Forge marketplace.

## Available Commands

### 1. `load_github_apps` - Simple GitHub Loader (Recommended)

This command loads apps from the buildly-marketplace GitHub organization using the public API (no token required).

**Usage:**
```bash
# Preview what would be imported (dry run)
python manage.py load_github_apps --dry-run --limit 10

# Import up to 10 apps from GitHub
python manage.py load_github_apps --limit 10

# Clear existing apps and import fresh ones
python manage.py load_github_apps --clear-existing --limit 5

# Import with custom pricing
python manage.py load_github_apps --price-cents 2900  # $29.00 per app
```

**Options:**
- `--limit N`: Maximum number of apps to import (default: 10)
- `--price-cents N`: Price in cents for all apps (default: 4900 = $49.00)
- `--clear-existing`: Remove all existing apps before importing
- `--dry-run`: Show what would be imported without making changes

### 2. `import_marketplace_repos` - Advanced Importer

This is the full-featured importer that requires a GitHub API token for enhanced functionality.

**Setup:**
```bash
export GITHUB_API_TOKEN="your_github_token_here"
```

**Usage:**
```bash
# Preview import with token-based API
python manage.py import_marketplace_repos --dry-run --limit 5

# Import with validation
python manage.py import_marketplace_repos --validate --limit 10

# Skip existing apps
python manage.py import_marketplace_repos --skip-existing
```

## Quick Start

For development and testing, use the simple loader:

```bash
# 1. Clear any test data and import real GitHub apps
python manage.py load_github_apps --clear-existing --limit 5

# 2. Start the server
python manage.py runserver

# 3. Visit http://localhost:8000/marketplace/ to see the apps
```

## App Categories

The loader automatically determines app categories based on repository names and descriptions:

- **api**: REST APIs, GraphQL endpoints
- **web**: Frontend applications, UI components
- **dashboard**: Admin panels, management interfaces
- **analytics**: Metrics, KPI tracking, reporting
- **service**: Microservices, backend services
- **utility**: Tools, utilities, helpers
- **crm**: Customer relationship management
- **reporting**: Document generation, reports
- **logic**: Business logic services
- **communication**: Chat, messaging, notifications

## Real GitHub Repositories

The loader fetches from the `buildly-marketplace` GitHub organization, which contains real Buildly-compatible applications:

- **Reporting**: FastAPI based reporting tool
- **Logic Service**: Django microservice template
- **CRM Service**: Contact and appointment management
- **Backstage**: Developer portal platform
- **BabbleBeaver**: Multi-LLM AI platform
- **KPI Service**: Project KPI tracking

## API Testing

After importing, test the API endpoints:

```bash
# List all apps
curl http://localhost:8000/marketplace/api/apps/

# Get app details
curl http://localhost:8000/marketplace/api/apps/reporting/
```

## Next Steps

1. **Customize Descriptions**: Use Django admin to improve app descriptions
2. **Add Screenshots**: Upload screenshots for better visual appeal  
3. **Update Pricing**: Adjust pricing per app in the admin interface
4. **Run Validation**: Use `validate_forge_repos` to check repository compliance
5. **Production Setup**: Configure `GITHUB_API_TOKEN` for production use