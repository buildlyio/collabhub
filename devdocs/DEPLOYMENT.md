# Production Environment Variables

For production deployment, the following environment variables must be set:

## Database Configuration
- `DB_NAME`: MySQL database name (default: defaultdb)
- `DB_USER`: MySQL database user (default: doadmin) 
- `DB_PASSWORD`: MySQL database password (REQUIRED - no default)
- `DB_HOST`: MySQL database host (default: db-mysql-nyc3-40163-do-user-2508039-0.m.db.ondigitalocean.com)
- `DB_PORT`: MySQL database port (default: 25060)

## Django Settings
- `DJANGO_SETTINGS_MODULE`: Django settings module (default: mysite.settings.production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Example Production Configuration
```bash
export DB_PASSWORD="your-secure-database-password"
export DB_NAME="defaultdb"
export DB_USER="doadmin"
export ALLOWED_HOSTS="collab.buildly.io,market.buildly.io"
```

## Deployment
The `scripts/init_django.sh` script will:
1. Run database migrations
2. Collect static files
3. Initialize comprehensive onboarding content (105+ resources and 6 certification quizzes)

## Required Management Commands for Production

After deployment, run these commands to set up the assessment system:

```bash
# Set environment
export DJANGO_SETTINGS_MODULE=mysite.settings.production

# Create the Developer Level Assessment quiz (18 questions)
python manage.py create_developer_level_quiz

# Create learning resources for all assessment topics
python manage.py create_learning_resources
```

**Important:** The Developer Assessment will not work until `create_developer_level_quiz` is run in production.

## Onboarding Content
The initialization script creates:
- Resources for Frontend, Backend, AI, Marketing, and Product Management developers
- Certification quizzes with essay questions
- Links to Buildly documentation, GitHub repositories, and learning materials
- Support for the 3-month developer onboarding journey