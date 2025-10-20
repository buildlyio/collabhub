from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from forge.models import ForgeApp
from forge.services import GitHubRepoValidationService
import requests
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import all repositories from buildly-marketplace GitHub organization as Forge products'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--github-token',
            type=str,
            help='GitHub API token (will use GITHUB_API_TOKEN env var if not provided)'
        )
        parser.add_argument(
            '--price-cents',
            type=int,
            default=4900,  # $49.00
            help='Price in cents for all imported apps (default: 4900 = $49.00)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without creating anything'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip repositories that already exist as Forge apps'
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Run validation on imported apps'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of repos to import (for testing)'
        )
    
    def handle(self, *args, **options):
        # Get GitHub token
        github_token = options.get('github_token') or getattr(settings, 'GITHUB_API_TOKEN', None)
        if not github_token:
            self.stdout.write(
                self.style.ERROR('GitHub token required. Set GITHUB_API_TOKEN env var or use --github-token')
            )
            return
        
        # Set up GitHub API headers
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CollabHub-Forge-Importer/1.0'
        }
        
        self.stdout.write('Fetching repositories from buildly-marketplace organization...')
        
        try:
            # Fetch all repositories from the organization
            repos = self._fetch_all_repos(headers)
            
            if options['limit']:
                repos = repos[:options['limit']]
                self.stdout.write(f'Limited to first {options["limit"]} repositories')
            
            self.stdout.write(f'Found {len(repos)} repositories to process')
            
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
                self._show_dry_run_preview(repos, options)
                return
            
            # Import repositories
            imported_apps = self._import_repositories(repos, options, headers)
            
            # Run validation if requested
            if options['validate'] and imported_apps:
                self.stdout.write('\nRunning validation on imported apps...')
                self._validate_imported_apps(imported_apps)
            
            # Summary
            self._show_import_summary(imported_apps, options)
            
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))
    
    def _fetch_all_repos(self, headers):
        """Fetch all repositories from buildly-marketplace organization"""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f'https://api.github.com/orgs/buildly-marketplace/repos'
            params = {
                'type': 'all',
                'sort': 'updated',
                'direction': 'desc',
                'per_page': per_page,
                'page': page
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 403:
                # Rate limit hit
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                current_time = int(time.time())
                wait_time = max(reset_time - current_time, 60)
                
                self.stdout.write(f'Rate limit hit. Waiting {wait_time} seconds...')
                time.sleep(wait_time)
                continue
            
            if response.status_code != 200:
                raise Exception(f'GitHub API error: {response.status_code} - {response.text}')
            
            page_repos = response.json()
            if not page_repos:
                break
            
            repos.extend(page_repos)
            self.stdout.write(f'Fetched page {page} ({len(page_repos)} repos)')
            
            page += 1
            
            # Be nice to GitHub API
            time.sleep(0.5)
        
        return repos
    
    def _show_dry_run_preview(self, repos, options):
        """Show what would be imported in dry run mode"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('DRY RUN PREVIEW')
        self.stdout.write('='*60)
        
        for i, repo in enumerate(repos, 1):
            slug = slugify(repo['name'])
            
            # Check if already exists
            exists = ForgeApp.objects.filter(slug=slug).exists()
            status = 'EXISTS' if exists else 'NEW'
            
            if exists and options['skip_existing']:
                status += ' (SKIP)'
            
            self.stdout.write(f'{i:3d}. {repo["name"]} -> {slug} [{status}]')
            self.stdout.write(f'     URL: {repo["html_url"]}')
            self.stdout.write(f'     Description: {repo["description"] or "No description"}')
            self.stdout.write(f'     Price: ${options["price_cents"]/100:.2f}')
            self.stdout.write('')
    
    def _import_repositories(self, repos, options, headers):
        """Import repositories as Forge apps"""
        imported_apps = []
        skipped_count = 0
        error_count = 0
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('IMPORTING REPOSITORIES')
        self.stdout.write('='*60)
        
        for i, repo in enumerate(repos, 1):
            try:
                self.stdout.write(f'{i:3d}/{len(repos)}: {repo["name"]}', ending=' ')
                
                slug = slugify(repo['name'])
                
                # Check if already exists
                if ForgeApp.objects.filter(slug=slug).exists():
                    if options['skip_existing']:
                        self.stdout.write(self.style.WARNING('SKIPPED (exists)'))
                        skipped_count += 1
                        continue
                    else:
                        self.stdout.write(self.style.WARNING('EXISTS (updating)'))
                
                # Get additional repository details
                repo_details = self._get_repository_details(repo, headers)
                
                # Create or update Forge app
                app = self._create_forge_app(repo, repo_details, options)
                imported_apps.append(app)
                
                self.stdout.write(self.style.SUCCESS('IMPORTED'))
                
                # Be nice to GitHub API
                time.sleep(0.5)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to import {repo['name']}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'ERROR: {str(e)}'))
        
        self.stdout.write(f'\nImport completed:')
        self.stdout.write(f'  Imported: {len(imported_apps)}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Errors: {error_count}')
        
        return imported_apps
    
    def _get_repository_details(self, repo, headers):
        """Get additional repository details from GitHub API"""
        # Get README content for better description
        readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
        readme_response = requests.get(readme_url, headers=headers)
        
        readme_content = None
        if readme_response.status_code == 200:
            import base64
            readme_data = readme_response.json()
            readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
        
        # Get topics (used as categories)
        topics = repo.get('topics', [])
        
        # Get latest release
        releases_url = f"https://api.github.com/repos/{repo['full_name']}/releases/latest"
        releases_response = requests.get(releases_url, headers=headers)
        
        latest_release = None
        if releases_response.status_code == 200:
            latest_release = releases_response.json()
        
        return {
            'readme_content': readme_content,
            'topics': topics,
            'latest_release': latest_release
        }
    
    def _create_forge_app(self, repo, repo_details, options):
        """Create or update a Forge app from repository data"""
        slug = slugify(repo['name'])
        
        # Extract summary from description or README
        summary = repo.get('description', '').strip()
        if not summary and repo_details['readme_content']:
            # Try to extract first paragraph from README
            lines = repo_details['readme_content'].split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('!'):
                    summary = line[:200] + '...' if len(line) > 200 else line
                    break
        
        if not summary:
            summary = f"Buildly-compatible application: {repo['name']}"
        
        # Determine categories from topics
        categories = []
        topic_to_category = {
            'api': 'api',
            'web': 'web',
            'dashboard': 'dashboard',
            'analytics': 'analytics',
            'auth': 'authentication',
            'authentication': 'authentication',
            'database': 'database',
            'storage': 'storage',
            'notification': 'communication',
            'chat': 'communication',
            'email': 'communication',
            'payment': 'payment',
            'ecommerce': 'ecommerce',
            'cms': 'cms',
            'blog': 'cms',
            'monitoring': 'monitoring',
            'logging': 'monitoring',
            'deployment': 'devops',
            'docker': 'devops',
            'kubernetes': 'devops',
            'k8s': 'devops',
            'utility': 'utility',
            'tool': 'utility',
            'microservice': 'service',
            'service': 'service'
        }
        
        for topic in repo_details['topics']:
            if topic.lower() in topic_to_category:
                categories.append(topic_to_category[topic.lower()])
        
        # Default categories if none found
        if not categories:
            categories = ['service', 'utility']
        
        # Remove duplicates and limit to 3
        categories = list(set(categories))[:3]
        
        # Determine license
        license_type = 'mit'  # Default
        if repo.get('license'):
            license_name = repo['license'].get('key', '').lower()
            license_mapping = {
                'mit': 'mit',
                'apache-2.0': 'apache2',
                'gpl-3.0': 'gpl3',
                'bsd-3-clause': 'bsd',
                'mpl-2.0': 'mozilla'
            }
            license_type = license_mapping.get(license_name, 'other')
        
        # Get last update date
        updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        
        # Create/update the app
        app, created = ForgeApp.objects.update_or_create(
            slug=slug,
            defaults={
                'name': repo['name'].replace('-', ' ').replace('_', ' ').title(),
                'summary': summary,
                'price_cents': options['price_cents'],
                'repo_url': repo['html_url'],
                'repo_owner': 'buildly-marketplace',
                'repo_name': repo['name'],
                'license_type': license_type,
                'change_date_utc': updated_at,
                'categories': categories,
                'targets': ['docker'],  # All apps are Docker deployable
                'is_published': True,
                'logo_url': f'https://via.placeholder.com/200x200/4A90E2/FFFFFF?text={repo["name"][:3].upper()}',
                'screenshots': [
                    'https://via.placeholder.com/800x600/F5F5F5/666666?text=Screenshot+Coming+Soon'
                ]
            }
        )
        
        return app
    
    def _validate_imported_apps(self, imported_apps):
        """Run validation on imported apps"""
        validator = GitHubRepoValidationService()
        
        for app in imported_apps:
            try:
                self.stdout.write(f'Validating {app.slug}...', ending=' ')
                
                validation = validator.validate_repository(
                    owner=app.repo_owner,
                    repo=app.repo_name,
                    forge_app=app
                )
                
                if validation.status == 'valid':
                    self.stdout.write(self.style.SUCCESS('VALID'))
                elif validation.status == 'invalid':
                    self.stdout.write(self.style.WARNING('INVALID'))
                    if validation.missing_items:
                        for item in validation.missing_items[:3]:  # Show first 3
                            self.stdout.write(f'  - Missing: {item}')
                else:
                    self.stdout.write(self.style.ERROR(f'ERROR ({validation.status})'))
                
                # Brief pause between validations
                time.sleep(1)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'FAILED: {str(e)}'))
                logger.error(f"Validation failed for {app.slug}: {str(e)}")
    
    def _show_import_summary(self, imported_apps, options):
        """Show final import summary"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('IMPORT SUMMARY')
        self.stdout.write('='*60)
        
        total_value = len(imported_apps) * options['price_cents']
        
        self.stdout.write(f'Successfully imported {len(imported_apps)} Forge apps')
        self.stdout.write(f'Total marketplace value: ${total_value/100:.2f}')
        self.stdout.write(f'Price per app: ${options["price_cents"]/100:.2f}')
        
        if imported_apps:
            self.stdout.write('\nImported apps:')
            for app in imported_apps:
                self.stdout.write(f'  • {app.name} ({app.slug})')
                self.stdout.write(f'    Categories: {", ".join(app.categories)}')
                self.stdout.write(f'    URL: {app.repo_url}')
        
        self.stdout.write('\nAPI endpoints to browse apps:')
        self.stdout.write('  GET /forge/api/apps/ - List all apps')
        self.stdout.write('  GET /forge/api/apps/{slug}/ - App details')
        
        self.stdout.write('\nAdmin interface:')
        self.stdout.write('  /admin/forge/ - Manage Forge apps')
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Review imported apps in Django admin')
        self.stdout.write('  2. Update descriptions and screenshots as needed')
        self.stdout.write('  3. Run validation: python manage.py validate_forge_repos')
        self.stdout.write('  4. Test API endpoints')
        
        if not options.get('validate'):
            self.stdout.write('\nTo validate repositories:')
            self.stdout.write('  python manage.py validate_forge_repos --published-only')