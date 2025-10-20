#!/usr/bin/env python3
"""
Simple GitHub Apps Loader for Forge Marketplace

This script loads real apps from the buildly-marketplace GitHub organization
without requiring API tokens (uses public API).
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from forge.models import ForgeApp
import requests
import time


class Command(BaseCommand):
    help = 'Load apps from buildly-marketplace GitHub organization (public API)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of apps to import (default: 10)'
        )
        parser.add_argument(
            '--price-cents',
            type=int,
            default=4900,
            help='Price in cents for imported apps (default: 4900 = $49)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing Forge apps before importing'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )

    def handle(self, *args, **options):
        if options['clear_existing'] and not options['dry_run']:
            existing_count = ForgeApp.objects.count()
            ForgeApp.objects.all().delete()
            self.stdout.write(f'Cleared {existing_count} existing apps')

        # Fetch repositories from buildly-marketplace
        self.stdout.write('Fetching repositories from buildly-marketplace...')
        
        try:
            url = 'https://api.github.com/orgs/buildly-marketplace/repos'
            params = {
                'per_page': options['limit'],
                'sort': 'updated',
                'direction': 'desc'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            repos = response.json()
            
            self.stdout.write(f'Found {len(repos)} repositories')
            
            if options['dry_run']:
                self._show_dry_run_preview(repos, options)
                return
            
            imported_count = 0
            skipped_count = 0
            
            for repo in repos:
                try:
                    app, created = self._import_repository(repo, options)
                    if created:
                        self.stdout.write(f'✓ Imported: {app.name}')
                        imported_count += 1
                    else:
                        self.stdout.write(f'- Updated: {app.name}')
                        imported_count += 1
                        
                except Exception as e:
                    self.stdout.write(f'✗ Failed to import {repo["name"]}: {e}')
                    skipped_count += 1
                
                # Be nice to GitHub API
                time.sleep(0.2)
            
            self._show_summary(imported_count, skipped_count, options)
            
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch repositories: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {e}'))

    def _show_dry_run_preview(self, repos, options):
        """Show what would be imported"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('DRY RUN PREVIEW')
        self.stdout.write('='*60)
        
        for i, repo in enumerate(repos, 1):
            name = repo['name']
            slug = slugify(name)
            description = repo.get('description') or 'No description available'
            exists = ForgeApp.objects.filter(slug=slug).exists()
            status = 'UPDATE' if exists else 'NEW'
            
            self.stdout.write(f'{i:2d}. {name} -> {slug} [{status}]')
            self.stdout.write(f'    URL: {repo["html_url"]}')
            self.stdout.write(f'    Description: {description[:80]}...')
            self.stdout.write(f'    Price: ${options["price_cents"]/100:.2f}')
            self.stdout.write('')

    def _import_repository(self, repo, options):
        """Import a single repository as a Forge app"""
        name = repo['name']
        slug = slugify(name)
        description = repo.get('description') or f'Buildly-compatible application: {name}'
        
        # Determine categories from repo name and description
        categories = self._determine_categories(name, description)
        
        # Determine license
        license_type = 'mit'  # Default
        if repo.get('license'):
            license_key = repo['license'].get('key', '').lower()
            license_mapping = {
                'mit': 'mit',
                'apache-2.0': 'apache2',
                'gpl-3.0': 'gpl3',
                'bsd-3-clause': 'bsd'
            }
            license_type = license_mapping.get(license_key, 'other')
        
        app_data = {
            'name': name.replace('-', ' ').replace('_', ' ').title(),
            'summary': description[:500],  # Ensure it fits in the field
            'price_cents': options['price_cents'],
            'repo_url': repo['html_url'],
            'repo_owner': 'Buildly-Marketplace',
            'repo_name': name,
            'license_type': license_type,
            'categories': categories,
            'targets': ['docker'],  # All buildly apps are Docker deployable
            'is_published': True
        }
        
        app, created = ForgeApp.objects.update_or_create(
            slug=slug,
            defaults=app_data
        )
        
        return app, created

    def _determine_categories(self, name, description):
        """Determine categories based on repository name and description"""
        text = f"{name} {description}".lower()
        
        categories = []
        
        # Category keywords mapping
        category_keywords = {
            'api': ['api', 'rest', 'graphql', 'endpoint'],
            'web': ['web', 'frontend', 'ui', 'interface'],
            'dashboard': ['dashboard', 'admin', 'panel'],
            'analytics': ['analytics', 'metrics', 'stats', 'kpi'],
            'service': ['service', 'microservice', 'server'],
            'utility': ['util', 'tool', 'helper'],
            'crm': ['crm', 'customer', 'relationship'],
            'reporting': ['report', 'reporting', 'document'],
            'logic': ['logic', 'business', 'rule'],
            'communication': ['chat', 'message', 'notification']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        # Default categories if none found
        if not categories:
            categories = ['service', 'utility']
        
        # Limit to 3 categories
        return categories[:3]

    def _show_summary(self, imported_count, skipped_count, options):
        """Show import summary"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('IMPORT SUMMARY')
        self.stdout.write('='*60)
        
        total_value = imported_count * options['price_cents']
        
        self.stdout.write(f'Successfully processed {imported_count} apps')
        self.stdout.write(f'Skipped: {skipped_count}')
        self.stdout.write(f'Total marketplace value: ${total_value/100:.2f}')
        
        total_published = ForgeApp.objects.filter(is_published=True).count()
        self.stdout.write(f'Total published apps in marketplace: {total_published}')
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Visit /marketplace/ to see the imported apps')
        self.stdout.write('  2. Update app descriptions and screenshots in Django admin')
        self.stdout.write('  3. Test the API: curl http://localhost:8000/marketplace/api/apps/')
        self.stdout.write('  4. Run validation: python manage.py validate_forge_repos')