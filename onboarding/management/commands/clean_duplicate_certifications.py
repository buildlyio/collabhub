from django.core.management.base import BaseCommand
from onboarding.models import Resource


class Command(BaseCommand):
    help = 'Remove duplicate certification resources'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up duplicate resources...')
        total_removed = 0
        
        # Find and remove duplicate Resources by title
        self.stdout.write('\nChecking Resources...')
        
        # Get all unique titles
        seen_titles = {}
        all_resources = Resource.objects.all().order_by('id')
        
        for resource in all_resources:
            key = (resource.team_member_type, resource.title)
            
            if key in seen_titles:
                # This is a duplicate, delete it
                resource.delete()
                total_removed += 1
                self.stdout.write(f'  ✓ Removed duplicate: {resource.title}')
            else:
                # First time seeing this, keep it
                seen_titles[key] = resource.id
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Cleanup complete! Removed {total_removed} duplicate resources.'))
