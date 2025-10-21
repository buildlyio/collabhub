# Environment Variables Configuration

This application uses environment variables for configuration. Copy `.env.example` to `.env` and configure the variables based on your deployment environment.

```bash
cp .env.example .env
```

## Required Environment Variables

### Core Django Settings
- `DJANGO_SETTINGS_MODULE`: Django settings module to use
  - Development: `mysite.settings.dev`
  - Production: `mysite.settings.production`
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames

### Stripe Payment Configuration (REQUIRED for Marketplace)
The marketplace requires Stripe for payment processing:

- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key (pk_test_... or pk_live_...)
- `STRIPE_SECRET_KEY`: Your Stripe secret key (sk_test_... or sk_live_...)
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook endpoint secret (whsec_...)

**To get Stripe keys:**
1. Create account at [stripe.com](https://stripe.com)
2. Go to Developers > API keys
3. Copy your publishable and secret keys
4. Set up webhook endpoint for payment processing

### GitHub Integration (REQUIRED for Repository Features)
- `GITHUB_KEY`: GitHub OAuth App Client ID
- `GITHUB_SECRET`: GitHub OAuth App Client Secret  
- `GITHUB_API_TOKEN`: Personal Access Token for GitHub API

**To set up GitHub OAuth:**
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth App with callback URL: `http://localhost:8000/accounts/github/login/callback/`
3. Copy Client ID and Client Secret

## Optional Environment Variables

### Database (Production Only)
Development uses SQLite by default. Production can use MySQL:
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port (default: 3306)

### Email Configuration (Production)
- `SENDGRID_API_KEY`: SendGrid API key for email delivery
- `SENDGRID_PASSWORD`: SendGrid password

### File Storage (Production)
- `SPACES_SECRET`: DigitalOcean Spaces secret key for static file storage

### API Integrations (Optional)
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `GOOGLE_PLACES_API_KEY`: Google Places API for location features
- `YELP_API_KEY`: Yelp API for business data

### Buildly Labs Integration (Optional)
- `LABS_TOKEN_URL`: Buildly Labs API URL (default: https://labs-api.buildly.dev)
- `LABS_CLIENT_ID`: Labs client ID
- `LABS_CLIENT_SECRET`: Labs client secret

### Marketplace Configuration
- `FORGE_MARKETPLACE_ORG`: GitHub organization for marketplace repos (default: buildly-marketplace)
- `FRONTEND_URL`: Base URL for payment redirects

## Development vs Production

### Development (.env for local development)
```env
DJANGO_SETTINGS_MODULE=mysite.settings.dev
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key
STRIPE_SECRET_KEY=sk_test_your_test_key
```

### Production (.env for production deployment)
```env
DJANGO_SETTINGS_MODULE=mysite.settings.production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_key
STRIPE_SECRET_KEY=sk_live_your_live_key
DB_PASSWORD=your_secure_database_password
```

## Security Notes

1. **Never commit `.env` files to version control**
2. **Use strong, unique passwords in production**
3. **Rotate API keys regularly**
4. **Use Stripe test keys for development**
5. **Set DEBUG=False in production**
6. **Use HTTPS in production (SOCIAL_AUTH_REDIRECT_IS_HTTPS=True)**

## Quick Start

For development with marketplace functionality:

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Set required Stripe keys in `.env`:
   ```env
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   ```

3. Optionally set GitHub keys for repository features:
   ```env
   GITHUB_KEY=your_github_oauth_app_key
   GITHUB_SECRET=your_github_oauth_app_secret
   ```

4. Start development server:
   ```bash
   python manage.py runserver
   ```

The marketplace will work with just the Stripe keys configured. Other integrations are optional and can be added as needed.