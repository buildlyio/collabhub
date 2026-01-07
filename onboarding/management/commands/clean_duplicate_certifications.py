from django.core.management.base import BaseCommand
from django.db.models import Count
from onboarding.models import Resource, Quiz, QuizQuestion


class Command(BaseCommand):
    help = 'Remove duplicate certification resources, quizzes, and quiz questions'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up duplicate certification data...')
        
        # Find and remove duplicate Resources
        self.stdout.write('\nChecking Resources...')
        resource_titles = Resource.objects.values('team_member_type', 'title').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for item in resource_titles:
            team_type = item['team_member_type']
            title = item['title']
            duplicates = Resource.objects.filter(
                team_member_type=team_type,
                title=title
            ).order_by('id')
            
            # Keep the first one, delete the rest
            keep = duplicates.first()
            to_delete = duplicates.exclude(id=keep.id)
            count = to_delete.count()
            
            if count > 0:
                to_delete.delete()
                self.stdout.write(f'  ✓ Removed {count} duplicate(s) of: {title}')
        
        # Find and remove duplicate Quizzes
        self.stdout.write('\nChecking Quizzes...')
        quiz_names = Quiz.objects.values('name').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for item in quiz_names:
            name = item['name']
            duplicates = Quiz.objects.filter(name=name).order_by('id')
            
            # Keep the first one, delete the rest (and their questions)
            keep = duplicates.first()
            to_delete = duplicates.exclude(id=keep.id)
            count = to_delete.count()
            
            if count > 0:
                to_delete.delete()
                self.stdout.write(f'  ✓ Removed {count} duplicate quiz(zes): {name}')
        
        # Remove orphaned QuizQuestions (questions without a quiz)
        self.stdout.write('\nChecking for orphaned QuizQuestions...')
        orphaned = QuizQuestion.objects.filter(quiz__isnull=True)
        orphaned_count = orphaned.count()
        if orphaned_count > 0:
            orphaned.delete()
            self.stdout.write(f'  ✓ Removed {orphaned_count} orphaned quiz questions')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Cleanup complete!'))
