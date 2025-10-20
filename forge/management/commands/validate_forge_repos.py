from django.core.management.base import BaseCommand
from forge.models import ForgeApp
from forge.services import GitHubRepoValidationService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate all Forge app repositories'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--app-id',
            type=str,
            help='Validate specific app by ID'
        )
        parser.add_argument(
            '--slug',
            type=str,
            help='Validate specific app by slug'
        )
        parser.add_argument(
            '--published-only',
            action='store_true',
            help='Only validate published apps'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force validation even if recently validated'
        )
    
    def handle(self, *args, **options):
        validator = GitHubRepoValidationService()
        
        # Filter apps based on options
        queryset = ForgeApp.objects.all()
        
        if options['app_id']:
            queryset = queryset.filter(id=options['app_id'])
        elif options['slug']:
            queryset = queryset.filter(slug=options['slug'])
        
        if options['published_only']:
            queryset = queryset.filter(is_published=True)
        
        if not queryset.exists():
            self.stdout.write(
                self.style.WARNING('No apps found matching criteria')
            )
            return
        
        self.stdout.write(f'Validating {queryset.count()} apps...')
        
        success_count = 0
        error_count = 0
        
        for app in queryset:
            try:
                self.stdout.write(f'Validating {app.slug}...', ending=' ')
                
                # Check if recently validated (unless force)
                if not options['force'] and app.latest_validation:
                    from django.utils import timezone
                    from datetime import timedelta
                    
                    if app.latest_validation.run_at > timezone.now() - timedelta(hours=1):
                        self.stdout.write(
                            self.style.WARNING('SKIPPED (recently validated)')
                        )
                        continue
                
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
                        for item in validation.missing_items:
                            self.stdout.write(f'  - Missing: {item}')
                else:
                    self.stdout.write(self.style.ERROR(f'ERROR ({validation.status})'))
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"Validation failed for {app.slug}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'FAILED: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Validation complete:')
        self.stdout.write(f'  Successful: {success_count}')
        self.stdout.write(f'  Errors: {error_count}')
        
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('All validations completed successfully!'))
        else:
            self.stdout.write(self.style.WARNING(f'{error_count} validations failed. Check logs for details.'))