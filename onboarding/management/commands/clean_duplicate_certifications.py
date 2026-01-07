from django.core.management.base import BaseCommand
from onboarding.models import Resource, Quiz, QuizQuestion


class Command(BaseCommand):
    help = 'Remove duplicate certification resources, quizzes, and quiz questions'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up duplicate certification data...')
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
        
        # Find and remove duplicate Quizzes by name
        self.stdout.write('\nChecking Quizzes...')
        
        seen_quizzes = {}
        all_quizzes = Quiz.objects.all().order_by('id')
        
        for quiz in all_quizzes:
            if quiz.name in seen_quizzes:
                # This is a duplicate, delete it (cascade will delete questions)
                quiz.delete()
                total_removed += 1
                self.stdout.write(f'  ✓ Removed duplicate quiz: {quiz.name}')
            else:
                # First time seeing this, keep it
                seen_quizzes[quiz.name] = quiz.id
        
        # Find and remove duplicate QuizQuestions
        self.stdout.write('\nChecking QuizQuestions...')
        
        seen_questions = {}
        all_questions = QuizQuestion.objects.all().order_by('id')
        
        for question in all_questions:
            if question.quiz_id:
                key = (question.quiz_id, question.question)
                
                if key in seen_questions:
                    # This is a duplicate, delete it
                    question.delete()
                    total_removed += 1
                    self.stdout.write(f'  ✓ Removed duplicate question')
                else:
                    # First time seeing this, keep it
                    seen_questions[key] = question.id
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Cleanup complete! Removed {total_removed} duplicate items.'))
