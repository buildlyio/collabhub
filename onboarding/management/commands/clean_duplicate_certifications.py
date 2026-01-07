from django.core.management.base import BaseCommand
from django.db import connection
from onboarding.models import Resource, Quiz


class Command(BaseCommand):
    help = 'Remove duplicate certification resources and quizzes'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up duplicate resources and quizzes...')
        total_removed = 0
        
        # Find and remove duplicate Resources by title
        self.stdout.write('\nChecking Resources...')
        
        seen_titles = {}
        all_resources = Resource.objects.all().order_by('id')
        
        for resource in all_resources:
            key = (resource.team_member_type, resource.title)
            
            if key in seen_titles:
                resource.delete()
                total_removed += 1
                self.stdout.write(f'  ✓ Removed duplicate: {resource.title}')
            else:
                seen_titles[key] = resource.id
        
        # Find and remove duplicate Quizzes by name using raw SQL to avoid cascade issues
        self.stdout.write('\nChecking Quizzes...')
        
        seen_quizzes = {}
        all_quizzes = Quiz.objects.all().order_by('id')
        ids_to_delete = []
        
        for quiz in all_quizzes:
            if quiz.name in seen_quizzes:
                # Mark for deletion
                ids_to_delete.append(quiz.id)
                self.stdout.write(f'  ✓ Marked duplicate quiz for deletion: {quiz.name}')
            else:
                seen_quizzes[quiz.name] = quiz.id
        
        # Delete duplicate quizzes using raw SQL to avoid cascade to missing table
        if ids_to_delete:
            with connection.cursor() as cursor:
                # First delete related quiz questions
                cursor.execute(
                    "DELETE FROM onboarding_quizquestion WHERE quiz_id IN (%s)" % ','.join(['%s'] * len(ids_to_delete)),
                    ids_to_delete
                )
                # Then delete the quizzes
                cursor.execute(
                    "DELETE FROM onboarding_quiz WHERE id IN (%s)" % ','.join(['%s'] * len(ids_to_delete)),
                    ids_to_delete
                )
                total_removed += len(ids_to_delete)
                self.stdout.write(f'  ✓ Removed {len(ids_to_delete)} duplicate quizzes')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Cleanup complete! Removed {total_removed} duplicate items.'))
