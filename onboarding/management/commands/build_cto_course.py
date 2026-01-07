from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from onboarding.models import (
    Resource, Quiz, QuizQuestion, TeamTraining, 
    TEAM_MEMBER_TYPES, Customer
)


class Command(BaseCommand):
    help = 'Populate CTO, Frontend, or Backend certification training data using existing models.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--track', 
            type=str, 
            choices=['cto', 'frontend', 'backend'], 
            default='cto', 
            help='Which certification track to create (cto|frontend|backend)'
        )
        parser.add_argument(
            '--customer-id',
            type=int,
            default=None,
            help='Customer ID to associate training with (optional, for public community training leave blank)'
        )

    def handle(self, *args, **options):
        track = options.get('track', 'cto')
        customer_id = options.get('customer_id')
        
        # Get or create a system user for ownership
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@buildly.io', 'is_staff': True}
        )
        
        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                raise CommandError(f'Customer with ID {customer_id} does not exist')
        
        # Call the appropriate track builder
        if track == 'cto':
            self.build_cto_certification(system_user, customer)
        elif track == 'frontend':
            self.build_frontend_certification(system_user, customer)
        elif track == 'backend':
            self.build_backend_certification(system_user, customer)
        
        self.stdout.write(self.style.SUCCESS(f'{track.upper()} certification created successfully!'))

    def build_cto_certification(self, owner, customer):
        """Create CTO certification resources, quizzes, and training modules."""
        self.stdout.write('Building CTO Certification...')
        
        # Module 1: Radical Transparency & Team Leadership
        module1_resources = []
        
        r1 = Resource.objects.create(
            team_member_type='all',
            title='What Makes a Great CTO',
            link='https://www.youtube.com/watch?v=nNSvMNyh4vs',
            descr='Video: Understanding the CTO role and responsibilities in modern software teams.'
        )
        module1_resources.append(r1)
        
        r2 = Resource.objects.create(
            team_member_type='all',
            title='Radical Candor by Kim Scott',
            link='https://www.youtube.com/watch?v=4yODalLQ2lM',
            descr='Video: Learn radical candor principles for effective team communication.'
        )
        module1_resources.append(r2)
        
        r3 = Resource.objects.create(
            team_member_type='all',
            title='Transparency Builds Stability - Gallup Research',
            link='http://www.gallup.com/workplace/236189/transparency-builds-stability-remote-workers.aspx',
            descr='Article: Research on how transparency impacts remote team stability and trust.'
        )
        module1_resources.append(r3)
        
        # Create Quiz for Module 1
        quiz1 = Quiz.objects.create(
            name='CTO Module 1: Radical Transparency Quiz',
            owner=owner,
            available_date=timezone.now().date(),
            url=f'https://collab.buildly.io/onboarding/quiz/cto-module-1-{timezone.now().timestamp()}'
        )
        
        QuizQuestion.objects.create(
            team_member_type='all',
            quiz=quiz1,
            question='What is an outcome of radical transparency in remote teams?',
            question_type='multiple_choice'
        )
        
        QuizQuestion.objects.create(
            team_member_type='all',
            quiz=quiz1,
            question='Describe how you would implement radical transparency in a distributed development team. Provide specific examples.',
            question_type='essay'
        )
        
        # Create Training for Module 1 (if customer provided)
        if customer:
            training1 = TeamTraining.objects.create(
                customer=customer,
                name='CTO Certification - Module 1: Radical Transparency',
                description='Learn the principles of radical transparency and how to lead remote development teams with trust and openness.',
                quiz=quiz1,
                start_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=14),
                is_active=True,
                created_by=owner
            )
            training1.resources.set(module1_resources)
            self.stdout.write(f'  Created: {training1.name}')
        
        # Module 2: Ethical AI & Technology Leadership
        module2_resources = []
        
        r4 = Resource.objects.create(
            team_member_type='all',
            title='Ethical AI by Harvard Business Review',
            link='https://www.youtube.com/watch?v=6zfhUe8H3Kw',
            descr='Video: Understanding ethical considerations in AI development and deployment.'
        )
        module2_resources.append(r4)
        
        quiz2 = Quiz.objects.create(
            name='CTO Module 2: Ethical AI Quiz',
            owner=owner,
            available_date=timezone.now().date(),
            url=f'https://collab.buildly.io/onboarding/quiz/cto-module-2-{timezone.now().timestamp()}'
        )
        
        QuizQuestion.objects.create(
            team_member_type='all',
            quiz=quiz2,
            question='What are the key ethical considerations when deploying AI systems in production?',
            question_type='essay'
        )
        
        if customer:
            training2 = TeamTraining.objects.create(
                customer=customer,
                name='CTO Certification - Module 2: Ethical AI',
                description='Explore ethical considerations, bias mitigation, and responsible AI practices for technical leaders.',
                quiz=quiz2,
                start_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=14),
                is_active=True,
                created_by=owner
            )
            training2.resources.set(module2_resources)
            self.stdout.write(f'  Created: {training2.name}')
        
        self.stdout.write(self.style.SUCCESS('  ✓ CTO certification modules created'))

    def build_frontend_certification(self, owner, customer):
        """Create Frontend Developer certification resources, quizzes, and training modules."""
        self.stdout.write('Building Frontend Developer Certification...')
        
        # Module 1: React & Modern Frontend
        module1_resources = []
        
        r1 = Resource.objects.create(
            team_member_type='community-frontend',
            title='React Official Documentation',
            link='https://react.dev/',
            descr='Official React documentation covering hooks, components, and best practices.'
        )
        module1_resources.append(r1)
        
        r2 = Resource.objects.create(
            team_member_type='community-frontend',
            title='TypeScript Handbook',
            link='https://www.typescriptlang.org/docs/handbook/intro.html',
            descr='Comprehensive guide to TypeScript for frontend developers.'
        )
        module1_resources.append(r2)
        
        quiz1 = Quiz.objects.create(
            name='Frontend Module 1: React & TypeScript Quiz',
            owner=owner,
            available_date=timezone.now().date(),
            url=f'https://collab.buildly.io/onboarding/quiz/frontend-module-1-{timezone.now().timestamp()}'
        )
        
        QuizQuestion.objects.create(
            team_member_type='community-frontend',
            quiz=quiz1,
            question='Explain the difference between controlled and uncontrolled components in React.',
            question_type='essay'
        )
        
        if customer:
            training1 = TeamTraining.objects.create(
                customer=customer,
                name='Frontend Certification - Module 1: React & TypeScript',
                description='Master React fundamentals, hooks, and TypeScript integration for modern web applications.',
                quiz=quiz1,
                start_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=14),
                is_active=True,
                created_by=owner
            )
            training1.resources.set(module1_resources)
            self.stdout.write(f'  Created: {training1.name}')
        
        self.stdout.write(self.style.SUCCESS('  ✓ Frontend certification modules created'))

    def build_backend_certification(self, owner, customer):
        """Create Backend Developer certification resources, quizzes, and training modules."""
        self.stdout.write('Building Backend Developer Certification...')
        
        # Module 1: Python & Django
        module1_resources = []
        
        r1 = Resource.objects.create(
            team_member_type='community-backend',
            title='Django Official Documentation',
            link='https://docs.djangoproject.com/en/stable/',
            descr='Official Django documentation for building scalable web applications.'
        )
        module1_resources.append(r1)
        
        r2 = Resource.objects.create(
            team_member_type='community-backend',
            title='RESTful API Design Best Practices',
            link='https://restfulapi.net/',
            descr='Guide to designing clean, maintainable REST APIs.'
        )
        module1_resources.append(r2)
        
        quiz1 = Quiz.objects.create(
            name='Backend Module 1: Django & REST APIs Quiz',
            owner=owner,
            available_date=timezone.now().date(),
            url=f'https://collab.buildly.io/onboarding/quiz/backend-module-1-{timezone.now().timestamp()}'
        )
        
        QuizQuestion.objects.create(
            team_member_type='community-backend',
            quiz=quiz1,
            question='Describe the Django ORM and how it differs from raw SQL queries. When would you use each?',
            question_type='essay'
        )
        
        if customer:
            training1 = TeamTraining.objects.create(
                customer=customer,
                name='Backend Certification - Module 1: Django & REST APIs',
                description='Learn Django framework fundamentals, ORM, and RESTful API design patterns.',
                quiz=quiz1,
                start_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=14),
                is_active=True,
                created_by=owner
            )
            training1.resources.set(module1_resources)
            self.stdout.write(f'  Created: {training1.name}')
        
        self.stdout.write(self.style.SUCCESS('  ✓ Backend certification modules created'))
