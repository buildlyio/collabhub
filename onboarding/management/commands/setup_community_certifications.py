"""
Management command to set up Community Certification tracks:
- Frontend Developer (Levels 1, 2, 3)
- Backend Developer (Levels 1, 2, 3)  
- Product Manager (Levels 1, 2, 3) - Focus on RAD Process

Each level requires:
- 6+ learning resources
- 3 quizzes
- 2 project submissions (reviewed by senior+ members)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from onboarding.models import (
    Resource, Quiz, QuizQuestion, CertificationLevel,
    TeamTraining, TrainingSection, TeamMember,
    CertificationTrack, CommunityCertificationLevel, CommunityBadge,
    CertificationProject, CertifiedReviewer, DeveloperPublicProfile,
    TEAM_MEMBER_TYPES
)


class Command(BaseCommand):
    help = 'Set up Community Certification tracks (Frontend, Backend, Product Manager)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing community certification data before setup',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Setting up Community Certifications...'))
        
        # Get admin user
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No superuser found. Please create one first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding admin user: {e}'))
            return

        if options['clear']:
            self.clear_existing_data()

        # Set up tracks
        self.setup_certification_tracks()
        
        # Set up community badges
        self.setup_community_badges()
        
        # Set up Frontend Certification
        self.setup_frontend_certification(admin_user)
        
        # Set up Backend Certification
        self.setup_backend_certification(admin_user)
        
        # Set up Product Manager Certification (RAD Process focus)
        self.setup_product_manager_certification(admin_user)
        
        # Set up initial reviewers (Greg, Radhika, David)
        self.setup_initial_reviewers()
        
        self.stdout.write(self.style.SUCCESS('✅ Community Certifications setup complete!'))

    def clear_existing_data(self):
        """Clear existing community certification data"""
        self.stdout.write('Clearing existing community certification data...')
        CertificationProject.objects.all().delete()
        CommunityCertificationLevel.objects.all().delete()
        CertificationTrack.objects.all().delete()
        CommunityBadge.objects.all().delete()
        CertifiedReviewer.objects.all().delete()
        self.stdout.write('  ✓ Cleared existing data')

    def setup_certification_tracks(self):
        """Create the three certification tracks"""
        self.stdout.write('Setting up certification tracks...')
        
        tracks_data = [
            {
                'key': 'frontend',
                'name': 'Frontend Developer',
                'description': 'Master modern frontend development with React, TypeScript, and best practices for building responsive, accessible web applications.',
                'icon': 'code',
                'color': '#3B82F6',  # Blue
                'order': 1,
            },
            {
                'key': 'backend',
                'name': 'Backend Developer',
                'description': 'Become proficient in backend development with Python/Django, REST APIs, databases, and scalable server architecture.',
                'icon': 'server',
                'color': '#10B981',  # Green
                'order': 2,
            },
            {
                'key': 'product_manager',
                'name': 'Product Manager',
                'description': 'Learn product management with a focus on RAD (Rapid Application Development) Process, agile methodologies, and stakeholder management.',
                'icon': 'clipboard-list',
                'color': '#8B5CF6',  # Purple
                'focus_methodology': 'RAD Process',
                'order': 3,
            },
        ]
        
        for track_data in tracks_data:
            track, created = CertificationTrack.objects.update_or_create(
                key=track_data['key'],
                defaults=track_data
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  ✓ {status} track: {track.name}')

    def setup_community_badges(self):
        """Create community achievement badges"""
        self.stdout.write('Setting up community badges...')
        
        badges_data = [
            {
                'key': 'first_contribution',
                'name': 'First Contribution',
                'description': 'Complete your first GitHub commit or pull request to an Open Build project.',
                'badge_type': 'contribution',
                'icon': '🌟',
                'color': '#FCD34D',
                'auto_award': True,
                'criteria_type': 'github_commits',
                'criteria_threshold': 1,
                'order': 1,
            },
            {
                'key': 'active_contributor',
                'name': 'Active Contributor',
                'description': 'Make 10+ commits and contribute regularly to Open Build projects.',
                'badge_type': 'contribution',
                'icon': '🚀',
                'color': '#60A5FA',
                'auto_award': True,
                'criteria_type': 'github_commits',
                'criteria_threshold': 10,
                'order': 2,
            },
            {
                'key': 'open_build_graduate',
                'name': 'Open Build Graduate',
                'description': 'Complete the Open Build development program and earn at least one Level 1 certification.',
                'badge_type': 'achievement',
                'icon': '🏆',
                'color': '#F59E0B',
                'auto_award': False,
                'order': 3,
            },
            {
                'key': 'community_leader',
                'name': 'Community Leader',
                'description': 'Mentor others and lead community projects. Must be a Level 3 certified member.',
                'badge_type': 'leadership',
                'icon': '👑',
                'color': '#EC4899',
                'auto_award': False,
                'order': 4,
            },
            {
                'key': 'elite_contributor',
                'name': 'Elite Contributor',
                'description': 'Make exceptional contributions with 50+ commits across multiple projects.',
                'badge_type': 'contribution',
                'icon': '💎',
                'color': '#6366F1',
                'auto_award': True,
                'criteria_type': 'github_commits',
                'criteria_threshold': 50,
                'order': 5,
            },
            {
                'key': 'problem_solver',
                'name': 'Problem Solver',
                'description': 'Help others by answering questions and resolving issues in the community.',
                'badge_type': 'achievement',
                'icon': '🎯',
                'color': '#14B8A6',
                'auto_award': False,
                'order': 6,
            },
        ]
        
        for badge_data in badges_data:
            badge, created = CommunityBadge.objects.update_or_create(
                key=badge_data['key'],
                defaults=badge_data
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  ✓ {status} badge: {badge.icon} {badge.name}')

    def setup_frontend_certification(self, admin_user):
        """Set up Frontend Developer certification levels"""
        self.stdout.write('\n📘 Setting up Frontend Developer Certification...')
        
        track = CertificationTrack.objects.get(key='frontend')
        
        # ============ LEVEL 1: Foundation ============
        self.stdout.write('  Level 1 - Foundation:')
        
        # Resources for Level 1
        l1_resources = []
        resources_l1_data = [
            ('React Official Documentation', 'https://react.dev/', 'Official React documentation covering components, hooks, and best practices.', 'community-frontend'),
            ('TypeScript Handbook', 'https://www.typescriptlang.org/docs/handbook/intro.html', 'Learn TypeScript fundamentals for type-safe JavaScript development.', 'community-frontend'),
            ('Tailwind CSS Documentation', 'https://tailwindcss.com/docs', 'Utility-first CSS framework for rapid UI development.', 'community-frontend'),
            ('MDN Web Docs - JavaScript', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide', 'Comprehensive JavaScript guide from Mozilla.', 'community-frontend'),
            ('React Hooks Guide', 'https://react.dev/reference/react', 'Complete reference for React Hooks API.', 'community-frontend'),
            ('CSS Flexbox & Grid Guide', 'https://css-tricks.com/snippets/css/complete-guide-grid/', 'Master CSS layout with Flexbox and Grid.', 'community-frontend'),
        ]
        
        for title, link, descr, member_type in resources_l1_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l1_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        # Quiz for Level 1
        quiz_l1_1, _ = Quiz.objects.get_or_create(
            name='Frontend Level 1 - React Fundamentals',
            defaults={
                'owner': admin_user,
                'available_date': date.today(),
                'url': 'https://collab.buildly.io/quiz/frontend-l1-react',
            }
        )
        quiz_l1_1.resources.set(l1_resources[:3])
        
        quiz_l1_2, _ = Quiz.objects.get_or_create(
            name='Frontend Level 1 - TypeScript Basics',
            defaults={
                'owner': admin_user,
                'available_date': date.today(),
                'url': 'https://collab.buildly.io/quiz/frontend-l1-typescript',
            }
        )
        
        quiz_l1_3, _ = Quiz.objects.get_or_create(
            name='Frontend Level 1 - CSS & Styling',
            defaults={
                'owner': admin_user,
                'available_date': date.today(),
                'url': 'https://collab.buildly.io/quiz/frontend-l1-css',
            }
        )
        
        # Create sample questions for quizzes
        self._create_quiz_questions(quiz_l1_1, [
            ('What is the purpose of React hooks?', 'essay', 'community-frontend'),
            ('Explain the difference between useState and useEffect.', 'essay', 'community-frontend'),
            ('How do you create a functional component in React?', 'essay', 'community-frontend'),
        ])
        
        self._create_quiz_questions(quiz_l1_2, [
            ('What are TypeScript interfaces and why are they useful?', 'essay', 'community-frontend'),
            ('Explain the difference between type and interface in TypeScript.', 'essay', 'community-frontend'),
        ])
        
        self._create_quiz_questions(quiz_l1_3, [
            ('Explain the CSS box model and its components.', 'essay', 'community-frontend'),
            ('What is the difference between Flexbox and CSS Grid? When would you use each?', 'essay', 'community-frontend'),
        ])
        
        # Create CertificationLevel for Level 1
        cert_level_1, _ = CertificationLevel.objects.get_or_create(
            name='Frontend Developer Level 1',
            defaults={
                'level_type': 'junior',
                'track': 'frontend',
                'description': 'Foundation level certification demonstrating understanding of React, TypeScript, and CSS fundamentals.',
                'requirements': 'Complete 6 resources, pass 3 quizzes with 70%+, submit 1 project.',
                'skills': 'React, TypeScript, CSS, Tailwind, JavaScript',
                'badge_color': '#3B82F6',
                'min_quiz_score': 70,
                'created_by': admin_user,
            }
        )
        cert_level_1.required_quizzes.set([quiz_l1_1, quiz_l1_2, quiz_l1_3])
        
        # Create CommunityCertificationLevel
        comm_level_1, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=1,
            defaults={
                'name': 'Frontend Developer Level 1 - Foundation',
                'description': 'Master React basics, TypeScript fundamentals, and CSS styling.',
                'required_resources_count': 6,
                'required_quizzes_count': 3,
                'required_projects_count': 1,
                'min_quiz_score': 70,
                'certification_level': cert_level_1,
                'badge_color': '#3B82F6',
                'min_reviewer_level': 2,
            }
        )
        comm_level_1.resources.set(l1_resources)
        comm_level_1.quizzes.set([quiz_l1_1, quiz_l1_2, quiz_l1_3])
        
        # Project placeholder for Level 1
        self._create_project_placeholder(comm_level_1, 
            'Build a React Component Library',
            'Create a small component library with at least 5 reusable React components using TypeScript and Tailwind CSS.',
            'small'
        )
        
        self.stdout.write(f'    ✓ Level 1 certification created')
        
        # ============ LEVEL 2: Practitioner ============
        self.stdout.write('  Level 2 - Practitioner:')
        
        l2_resources = []
        resources_l2_data = [
            ('Redux Toolkit Documentation', 'https://redux-toolkit.js.org/', 'Modern Redux state management with Redux Toolkit.', 'community-frontend'),
            ('React Testing Library', 'https://testing-library.com/docs/react-testing-library/intro/', 'Testing best practices for React applications.', 'community-frontend'),
            ('Web Performance Fundamentals', 'https://web.dev/performance/', 'Google\'s guide to web performance optimization.', 'community-frontend'),
            ('Next.js Documentation', 'https://nextjs.org/docs', 'React framework for production with SSR and SSG.', 'community-frontend'),
            ('React Query / TanStack Query', 'https://tanstack.com/query/latest', 'Data fetching and caching for React.', 'community-frontend'),
            ('Storybook Documentation', 'https://storybook.js.org/docs', 'UI component development and documentation tool.', 'community-frontend'),
            ('React Design Patterns', 'https://www.patterns.dev/react', 'Common design patterns for React applications.', 'community-frontend'),
            ('Vite Build Tool', 'https://vitejs.dev/guide/', 'Next generation frontend build tool.', 'community-frontend'),
        ]
        
        for title, link, descr, member_type in resources_l2_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l2_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        # Quizzes for Level 2
        quiz_l2_1, _ = Quiz.objects.get_or_create(
            name='Frontend Level 2 - State Management',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/frontend-l2-state'}
        )
        quiz_l2_2, _ = Quiz.objects.get_or_create(
            name='Frontend Level 2 - Testing',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/frontend-l2-testing'}
        )
        quiz_l2_3, _ = Quiz.objects.get_or_create(
            name='Frontend Level 2 - Performance',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/frontend-l2-performance'}
        )
        
        self._create_quiz_questions(quiz_l2_1, [
            ('Compare Redux, Context API, and Zustand. When would you choose each?', 'essay', 'community-frontend'),
            ('Explain how Redux Toolkit simplifies Redux development.', 'essay', 'community-frontend'),
        ])
        
        self._create_quiz_questions(quiz_l2_2, [
            ('What is the Testing Trophy and how does it apply to frontend testing?', 'essay', 'community-frontend'),
            ('Describe how you would test a React component that fetches data.', 'essay', 'community-frontend'),
        ])
        
        self._create_quiz_questions(quiz_l2_3, [
            ('What are Core Web Vitals and how do you optimize for them?', 'essay', 'community-frontend'),
            ('Explain code splitting and lazy loading in React.', 'essay', 'community-frontend'),
        ])
        
        cert_level_2, _ = CertificationLevel.objects.get_or_create(
            name='Frontend Developer Level 2',
            defaults={
                'level_type': 'intermediate',
                'track': 'frontend',
                'description': 'Practitioner level certification for state management, testing, and performance optimization.',
                'requirements': 'Complete 8 resources, pass 3 quizzes with 75%+, submit 2 projects.',
                'skills': 'Redux, Testing, Performance, Next.js, React Query',
                'badge_color': '#2563EB',
                'min_quiz_score': 75,
                'created_by': admin_user,
            }
        )
        cert_level_2.required_quizzes.set([quiz_l2_1, quiz_l2_2, quiz_l2_3])
        
        comm_level_2, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=2,
            defaults={
                'name': 'Frontend Developer Level 2 - Practitioner',
                'description': 'Master state management, testing strategies, and performance optimization.',
                'required_resources_count': 8,
                'required_quizzes_count': 3,
                'required_projects_count': 2,
                'min_quiz_score': 75,
                'certification_level': cert_level_2,
                'badge_color': '#2563EB',
                'min_reviewer_level': 2,
            }
        )
        comm_level_2.resources.set(l2_resources)
        comm_level_2.quizzes.set([quiz_l2_1, quiz_l2_2, quiz_l2_3])
        
        self._create_project_placeholder(comm_level_2, 
            'Build a Full-Stack Application with Testing',
            'Create a React application with state management, API integration, and comprehensive test coverage.',
            'medium'
        )
        self._create_project_placeholder(comm_level_2,
            'Performance Optimization Case Study',
            'Optimize an existing application for Core Web Vitals. Document before/after metrics.',
            'medium'
        )
        
        self.stdout.write(f'    ✓ Level 2 certification created')
        
        # ============ LEVEL 3: Senior ============
        self.stdout.write('  Level 3 - Senior:')
        
        l3_resources = []
        resources_l3_data = [
            ('Frontend Architecture Patterns', 'https://www.patterns.dev/', 'Design and rendering patterns for modern web apps.', 'community-frontend'),
            ('Web Accessibility Guidelines (WCAG)', 'https://www.w3.org/WAI/standards-guidelines/wcag/', 'Accessibility standards for inclusive web development.', 'community-frontend'),
            ('Micro-Frontends Architecture', 'https://micro-frontends.org/', 'Scaling frontend development with micro-frontends.', 'community-frontend'),
            ('React Server Components', 'https://react.dev/reference/rsc/server-components', 'Server-side React for improved performance.', 'community-frontend'),
            ('Frontend Security Best Practices', 'https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html', 'OWASP security guidelines for frontend.', 'community-frontend'),
            ('Design Systems Guide', 'https://www.designsystems.com/', 'Building and maintaining design systems.', 'community-frontend'),
            ('Technical Leadership', 'https://leaddev.com/', 'Resources for technical leadership and mentoring.', 'community-frontend'),
            ('CI/CD for Frontend', 'https://docs.github.com/en/actions', 'GitHub Actions for frontend deployment pipelines.', 'community-frontend'),
            ('Monorepo Management', 'https://turbo.build/repo/docs', 'Turborepo for managing monorepos at scale.', 'community-frontend'),
            ('Advanced TypeScript Patterns', 'https://www.typescriptlang.org/docs/handbook/2/types-from-types.html', 'Advanced TypeScript type manipulation.', 'community-frontend'),
        ]
        
        for title, link, descr, member_type in resources_l3_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l3_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        quiz_l3_1, _ = Quiz.objects.get_or_create(
            name='Frontend Level 3 - Architecture',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/frontend-l3-architecture'}
        )
        quiz_l3_2, _ = Quiz.objects.get_or_create(
            name='Frontend Level 3 - Accessibility',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/frontend-l3-a11y'}
        )
        quiz_l3_3, _ = Quiz.objects.get_or_create(
            name='Frontend Level 3 - Leadership',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/frontend-l3-leadership'}
        )
        
        self._create_quiz_questions(quiz_l3_1, [
            ('Design a frontend architecture for a large-scale e-commerce platform. Include state management, routing, and component organization.', 'essay', 'community-frontend'),
            ('How would you implement micro-frontends? What are the tradeoffs?', 'essay', 'community-frontend'),
        ])
        
        self._create_quiz_questions(quiz_l3_2, [
            ('Explain WCAG 2.1 AA compliance. How would you audit an existing application?', 'essay', 'community-frontend'),
            ('Describe how you would make a complex data visualization accessible.', 'essay', 'community-frontend'),
        ])
        
        self._create_quiz_questions(quiz_l3_3, [
            ('How would you mentor a junior developer struggling with React concepts?', 'essay', 'community-frontend'),
            ('Describe how you would lead a frontend team in adopting a new technology.', 'essay', 'community-frontend'),
        ])
        
        cert_level_3, _ = CertificationLevel.objects.get_or_create(
            name='Frontend Developer Level 3 (Senior)',
            defaults={
                'level_type': 'senior',
                'track': 'frontend',
                'description': 'Senior level certification for architecture, accessibility, and technical leadership.',
                'requirements': 'Complete 10 resources, pass 3 quizzes with 80%+, submit 2 complex projects, demonstrate mentoring.',
                'skills': 'Architecture, Accessibility, Leadership, Design Systems, Security',
                'badge_color': '#1D4ED8',
                'min_quiz_score': 80,
                'created_by': admin_user,
            }
        )
        cert_level_3.required_quizzes.set([quiz_l3_1, quiz_l3_2, quiz_l3_3])
        
        comm_level_3, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=3,
            defaults={
                'name': 'Frontend Developer Level 3 - Senior',
                'description': 'Master frontend architecture, accessibility, and lead teams.',
                'required_resources_count': 10,
                'required_quizzes_count': 3,
                'required_projects_count': 2,
                'min_quiz_score': 80,
                'certification_level': cert_level_3,
                'badge_color': '#1D4ED8',
                'min_reviewer_level': 3,
            }
        )
        comm_level_3.resources.set(l3_resources)
        comm_level_3.quizzes.set([quiz_l3_1, quiz_l3_2, quiz_l3_3])
        
        self._create_project_placeholder(comm_level_3,
            'Design System Implementation',
            'Build a comprehensive design system with accessibility compliance and documentation.',
            'complex'
        )
        self._create_project_placeholder(comm_level_3,
            'Mentorship Documentation',
            'Document your mentorship of a junior developer through a project, including code reviews and feedback.',
            'document'
        )
        
        self.stdout.write(f'    ✓ Level 3 certification created')

    def setup_backend_certification(self, admin_user):
        """Set up Backend Developer certification levels"""
        self.stdout.write('\n📗 Setting up Backend Developer Certification...')
        
        track = CertificationTrack.objects.get(key='backend')
        
        # ============ LEVEL 1: Foundation ============
        self.stdout.write('  Level 1 - Foundation:')
        
        l1_resources = []
        resources_l1_data = [
            ('Django Official Tutorial', 'https://docs.djangoproject.com/en/5.0/intro/tutorial01/', 'Official Django getting started tutorial.', 'community-backend'),
            ('Python Documentation', 'https://docs.python.org/3/tutorial/', 'Official Python 3 tutorial.', 'community-backend'),
            ('REST API Design Guide', 'https://restfulapi.net/', 'Best practices for RESTful API design.', 'community-backend'),
            ('PostgreSQL Tutorial', 'https://www.postgresqltutorial.com/', 'Comprehensive PostgreSQL database tutorial.', 'community-backend'),
            ('Django REST Framework', 'https://www.django-rest-framework.org/tutorial/quickstart/', 'Building Web APIs with Django REST Framework.', 'community-backend'),
            ('Git & GitHub Guide', 'https://docs.github.com/en/get-started/quickstart', 'Version control with Git and GitHub.', 'community-backend'),
        ]
        
        for title, link, descr, member_type in resources_l1_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l1_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        quiz_l1_1, _ = Quiz.objects.get_or_create(
            name='Backend Level 1 - Django Fundamentals',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l1-django'}
        )
        quiz_l1_2, _ = Quiz.objects.get_or_create(
            name='Backend Level 1 - REST API Design',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l1-api'}
        )
        quiz_l1_3, _ = Quiz.objects.get_or_create(
            name='Backend Level 1 - Database Basics',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l1-db'}
        )
        
        self._create_quiz_questions(quiz_l1_1, [
            ('Explain the Django MVT (Model-View-Template) pattern.', 'essay', 'community-backend'),
            ('How do Django migrations work and why are they important?', 'essay', 'community-backend'),
        ])
        
        self._create_quiz_questions(quiz_l1_2, [
            ('What are the HTTP methods and when should each be used in a REST API?', 'essay', 'community-backend'),
            ('Explain REST API best practices for URL structure and naming.', 'essay', 'community-backend'),
        ])
        
        self._create_quiz_questions(quiz_l1_3, [
            ('Explain the difference between SQL JOINs (INNER, LEFT, RIGHT, FULL).', 'essay', 'community-backend'),
            ('What is database normalization and why is it important?', 'essay', 'community-backend'),
        ])
        
        cert_level_1, _ = CertificationLevel.objects.get_or_create(
            name='Backend Developer Level 1',
            defaults={
                'level_type': 'junior',
                'track': 'backend',
                'description': 'Foundation level certification for Django, REST APIs, and databases.',
                'requirements': 'Complete 6 resources, pass 3 quizzes with 70%+, submit 1 project.',
                'skills': 'Python, Django, REST APIs, PostgreSQL, Git',
                'badge_color': '#10B981',
                'min_quiz_score': 70,
                'created_by': admin_user,
            }
        )
        cert_level_1.required_quizzes.set([quiz_l1_1, quiz_l1_2, quiz_l1_3])
        
        comm_level_1, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=1,
            defaults={
                'name': 'Backend Developer Level 1 - Foundation',
                'description': 'Master Django basics, REST API design, and database fundamentals.',
                'required_resources_count': 6,
                'required_quizzes_count': 3,
                'required_projects_count': 1,
                'min_quiz_score': 70,
                'certification_level': cert_level_1,
                'badge_color': '#10B981',
                'min_reviewer_level': 2,
            }
        )
        comm_level_1.resources.set(l1_resources)
        comm_level_1.quizzes.set([quiz_l1_1, quiz_l1_2, quiz_l1_3])
        
        self._create_project_placeholder(comm_level_1,
            'Build a REST API',
            'Create a Django REST API with CRUD operations, authentication, and documentation.',
            'small'
        )
        
        self.stdout.write(f'    ✓ Level 1 certification created')
        
        # ============ LEVEL 2: Practitioner ============
        self.stdout.write('  Level 2 - Practitioner:')
        
        l2_resources = []
        resources_l2_data = [
            ('Django Authentication', 'https://docs.djangoproject.com/en/5.0/topics/auth/', 'Django authentication system.', 'community-backend'),
            ('OAuth 2.0 Guide', 'https://oauth.net/2/', 'Understanding OAuth 2.0 for API security.', 'community-backend'),
            ('Pytest Documentation', 'https://docs.pytest.org/en/stable/', 'Python testing with pytest.', 'community-backend'),
            ('Redis Documentation', 'https://redis.io/docs/', 'In-memory data store for caching.', 'community-backend'),
            ('Celery Documentation', 'https://docs.celeryq.dev/en/stable/', 'Distributed task queue for Python.', 'community-backend'),
            ('Docker Documentation', 'https://docs.docker.com/get-started/', 'Containerization with Docker.', 'community-backend'),
            ('API Security Best Practices', 'https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html', 'OWASP REST security guidelines.', 'community-backend'),
            ('Django Signals', 'https://docs.djangoproject.com/en/5.0/topics/signals/', 'Django signals for decoupled applications.', 'community-backend'),
        ]
        
        for title, link, descr, member_type in resources_l2_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l2_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        quiz_l2_1, _ = Quiz.objects.get_or_create(
            name='Backend Level 2 - Authentication & Security',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l2-auth'}
        )
        quiz_l2_2, _ = Quiz.objects.get_or_create(
            name='Backend Level 2 - Testing',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l2-testing'}
        )
        quiz_l2_3, _ = Quiz.objects.get_or_create(
            name='Backend Level 2 - Caching & Performance',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l2-cache'}
        )
        
        self._create_quiz_questions(quiz_l2_1, [
            ('Explain JWT authentication and its security considerations.', 'essay', 'community-backend'),
            ('How would you implement role-based access control in Django?', 'essay', 'community-backend'),
        ])
        
        self._create_quiz_questions(quiz_l2_2, [
            ('What is the testing pyramid and how does it apply to backend development?', 'essay', 'community-backend'),
            ('How do you test Django views and API endpoints?', 'essay', 'community-backend'),
        ])
        
        self._create_quiz_questions(quiz_l2_3, [
            ('Explain caching strategies and when to use Redis vs Memcached.', 'essay', 'community-backend'),
            ('How would you identify and optimize slow database queries?', 'essay', 'community-backend'),
        ])
        
        cert_level_2, _ = CertificationLevel.objects.get_or_create(
            name='Backend Developer Level 2',
            defaults={
                'level_type': 'intermediate',
                'track': 'backend',
                'description': 'Practitioner level for authentication, testing, and performance.',
                'requirements': 'Complete 8 resources, pass 3 quizzes with 75%+, submit 2 projects.',
                'skills': 'Authentication, OAuth, Testing, Redis, Celery, Docker',
                'badge_color': '#059669',
                'min_quiz_score': 75,
                'created_by': admin_user,
            }
        )
        cert_level_2.required_quizzes.set([quiz_l2_1, quiz_l2_2, quiz_l2_3])
        
        comm_level_2, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=2,
            defaults={
                'name': 'Backend Developer Level 2 - Practitioner',
                'description': 'Master authentication, testing, and performance optimization.',
                'required_resources_count': 8,
                'required_quizzes_count': 3,
                'required_projects_count': 2,
                'min_quiz_score': 75,
                'certification_level': cert_level_2,
                'badge_color': '#059669',
                'min_reviewer_level': 2,
            }
        )
        comm_level_2.resources.set(l2_resources)
        comm_level_2.quizzes.set([quiz_l2_1, quiz_l2_2, quiz_l2_3])
        
        self._create_project_placeholder(comm_level_2,
            'Secure API with Authentication',
            'Build an API with JWT authentication, role-based permissions, and comprehensive tests.',
            'medium'
        )
        self._create_project_placeholder(comm_level_2,
            'Background Task System',
            'Implement a background task system with Celery and Redis for email or notification processing.',
            'medium'
        )
        
        self.stdout.write(f'    ✓ Level 2 certification created')
        
        # ============ LEVEL 3: Senior ============
        self.stdout.write('  Level 3 - Senior:')
        
        l3_resources = []
        resources_l3_data = [
            ('System Design Primer', 'https://github.com/donnemartin/system-design-primer', 'Learn how to design large-scale systems.', 'community-backend'),
            ('Microservices Patterns', 'https://microservices.io/patterns/', 'Patterns for microservices architecture.', 'community-backend'),
            ('Kubernetes Documentation', 'https://kubernetes.io/docs/tutorials/', 'Container orchestration with Kubernetes.', 'community-backend'),
            ('Database Scaling Strategies', 'https://aws.amazon.com/blogs/database/sharding-with-amazon-relational-database-service/', 'Scaling databases with sharding and replication.', 'community-backend'),
            ('Event-Driven Architecture', 'https://www.confluent.io/learn/event-driven-architecture/', 'Event streaming and messaging patterns.', 'community-backend'),
            ('Infrastructure as Code', 'https://www.terraform.io/intro', 'Terraform for infrastructure management.', 'community-backend'),
            ('API Gateway Patterns', 'https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html', 'API Gateway design and implementation.', 'community-backend'),
            ('Observability Guide', 'https://opentelemetry.io/docs/', 'OpenTelemetry for monitoring and tracing.', 'community-backend'),
            ('Technical Leadership', 'https://staffeng.com/', 'Resources for staff engineers and tech leads.', 'community-backend'),
            ('High Availability Patterns', 'https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/', 'AWS patterns for high availability.', 'community-backend'),
        ]
        
        for title, link, descr, member_type in resources_l3_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l3_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        quiz_l3_1, _ = Quiz.objects.get_or_create(
            name='Backend Level 3 - System Design',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l3-system'}
        )
        quiz_l3_2, _ = Quiz.objects.get_or_create(
            name='Backend Level 3 - DevOps & Scalability',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l3-devops'}
        )
        quiz_l3_3, _ = Quiz.objects.get_or_create(
            name='Backend Level 3 - Leadership',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/backend-l3-leadership'}
        )
        
        self._create_quiz_questions(quiz_l3_1, [
            ('Design a scalable backend architecture for a real-time chat application with millions of users.', 'essay', 'community-backend'),
            ('Explain CAP theorem and its implications for distributed systems.', 'essay', 'community-backend'),
        ])
        
        self._create_quiz_questions(quiz_l3_2, [
            ('How would you implement a CI/CD pipeline for a microservices architecture?', 'essay', 'community-backend'),
            ('Explain blue-green and canary deployment strategies.', 'essay', 'community-backend'),
        ])
        
        self._create_quiz_questions(quiz_l3_3, [
            ('How would you mentor a junior developer on writing clean, maintainable code?', 'essay', 'community-backend'),
            ('Describe how you would lead a team in migrating a monolith to microservices.', 'essay', 'community-backend'),
        ])
        
        cert_level_3, _ = CertificationLevel.objects.get_or_create(
            name='Backend Developer Level 3 (Senior)',
            defaults={
                'level_type': 'senior',
                'track': 'backend',
                'description': 'Senior level for system design, DevOps, and technical leadership.',
                'requirements': 'Complete 10 resources, pass 3 quizzes with 80%+, submit 2 complex projects.',
                'skills': 'System Design, Microservices, Kubernetes, DevOps, Leadership',
                'badge_color': '#047857',
                'min_quiz_score': 80,
                'created_by': admin_user,
            }
        )
        cert_level_3.required_quizzes.set([quiz_l3_1, quiz_l3_2, quiz_l3_3])
        
        comm_level_3, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=3,
            defaults={
                'name': 'Backend Developer Level 3 - Senior',
                'description': 'Master system design, scalability, and technical leadership.',
                'required_resources_count': 10,
                'required_quizzes_count': 3,
                'required_projects_count': 2,
                'min_quiz_score': 80,
                'certification_level': cert_level_3,
                'badge_color': '#047857',
                'min_reviewer_level': 3,
            }
        )
        comm_level_3.resources.set(l3_resources)
        comm_level_3.quizzes.set([quiz_l3_1, quiz_l3_2, quiz_l3_3])
        
        self._create_project_placeholder(comm_level_3,
            'System Design Document',
            'Create a comprehensive system design document for a scalable application.',
            'document'
        )
        self._create_project_placeholder(comm_level_3,
            'Mentorship Documentation',
            'Document your mentorship of a junior developer including code reviews and growth tracking.',
            'document'
        )
        
        self.stdout.write(f'    ✓ Level 3 certification created')

    def setup_product_manager_certification(self, admin_user):
        """Set up Product Manager certification with RAD Process focus"""
        self.stdout.write('\n📕 Setting up Product Manager Certification (RAD Process Focus)...')
        
        track = CertificationTrack.objects.get(key='product_manager')
        
        # ============ LEVEL 1: Foundation ============
        self.stdout.write('  Level 1 - Foundation:')
        
        l1_resources = []
        resources_l1_data = [
            ('RAD Process Introduction', 'https://buildly.io/rad-process', 'Introduction to Rapid Application Development process.', 'community-product'),
            ('Agile Manifesto & Principles', 'https://agilemanifesto.org/', 'The Agile Manifesto and its 12 principles.', 'community-product'),
            ('User Story Best Practices', 'https://www.atlassian.com/agile/project-management/user-stories', 'Writing effective user stories.', 'community-product'),
            ('Product Requirements Document Guide', 'https://www.productplan.com/learn/product-requirements-document/', 'How to write effective PRDs.', 'community-product'),
            ('Prioritization Frameworks', 'https://www.productplan.com/learn/prioritization-frameworks/', 'RICE, MoSCoW, and other frameworks.', 'community-product'),
            ('Stakeholder Communication', 'https://www.mindtools.com/pages/article/newPPM_07.htm', 'Effective stakeholder management.', 'community-product'),
        ]
        
        for title, link, descr, member_type in resources_l1_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l1_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        quiz_l1_1, _ = Quiz.objects.get_or_create(
            name='PM Level 1 - RAD Process Basics',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l1-rad'}
        )
        quiz_l1_2, _ = Quiz.objects.get_or_create(
            name='PM Level 1 - User Stories & Requirements',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l1-stories'}
        )
        quiz_l1_3, _ = Quiz.objects.get_or_create(
            name='PM Level 1 - Prioritization',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l1-priority'}
        )
        
        self._create_quiz_questions(quiz_l1_1, [
            ('Explain the core principles of the RAD (Rapid Application Development) process.', 'essay', 'community-product'),
            ('How does RAD differ from traditional Waterfall development?', 'essay', 'community-product'),
        ])
        
        self._create_quiz_questions(quiz_l1_2, [
            ('Write a user story for a login feature following INVEST criteria.', 'essay', 'community-product'),
            ('What should be included in a Product Requirements Document?', 'essay', 'community-product'),
        ])
        
        self._create_quiz_questions(quiz_l1_3, [
            ('Explain the RICE prioritization framework with an example.', 'essay', 'community-product'),
            ('How do you balance technical debt against new features?', 'essay', 'community-product'),
        ])
        
        cert_level_1, _ = CertificationLevel.objects.get_or_create(
            name='Product Manager Level 1',
            defaults={
                'level_type': 'junior',
                'track': 'product_manager',
                'description': 'Foundation level for RAD Process, user stories, and prioritization.',
                'requirements': 'Complete 6 resources, pass 3 quizzes with 70%+, submit 1 PRD.',
                'skills': 'RAD Process, User Stories, PRD, Prioritization, Stakeholder Management',
                'badge_color': '#8B5CF6',
                'min_quiz_score': 70,
                'created_by': admin_user,
            }
        )
        cert_level_1.required_quizzes.set([quiz_l1_1, quiz_l1_2, quiz_l1_3])
        
        comm_level_1, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=1,
            defaults={
                'name': 'Product Manager Level 1 - Foundation',
                'description': 'Master RAD Process basics, user stories, and prioritization.',
                'required_resources_count': 6,
                'required_quizzes_count': 3,
                'required_projects_count': 1,
                'min_quiz_score': 70,
                'certification_level': cert_level_1,
                'badge_color': '#8B5CF6',
                'min_reviewer_level': 2,
            }
        )
        comm_level_1.resources.set(l1_resources)
        comm_level_1.quizzes.set([quiz_l1_1, quiz_l1_2, quiz_l1_3])
        
        self._create_project_placeholder(comm_level_1,
            'Product Requirements Document',
            'Create a PRD for a new feature including user stories, acceptance criteria, and wireframes.',
            'document'
        )
        
        self.stdout.write(f'    ✓ Level 1 certification created')
        
        # ============ LEVEL 2: Practitioner ============
        self.stdout.write('  Level 2 - Practitioner:')
        
        l2_resources = []
        resources_l2_data = [
            ('RAD Process - Advanced Techniques', 'https://buildly.io/rad-advanced', 'Advanced RAD Process implementation.', 'community-product'),
            ('Product Roadmapping', 'https://www.productplan.com/learn/what-is-a-product-roadmap/', 'Building effective product roadmaps.', 'community-product'),
            ('Product Analytics', 'https://mixpanel.com/content/guide-to-product-analytics/', 'Guide to product analytics and metrics.', 'community-product'),
            ('OKRs Guide', 'https://www.whatmatters.com/get-started', 'Objectives and Key Results framework.', 'community-product'),
            ('User Research Methods', 'https://www.nngroup.com/articles/which-ux-research-methods/', 'UX research methods guide.', 'community-product'),
            ('Sprint Planning', 'https://www.scrum.org/resources/what-is-sprint-planning', 'Effective sprint planning techniques.', 'community-product'),
            ('A/B Testing Guide', 'https://www.optimizely.com/optimization-glossary/ab-testing/', 'A/B testing and experimentation.', 'community-product'),
            ('Competitive Analysis', 'https://www.productplan.com/learn/competitive-analysis/', 'Conducting competitive analysis.', 'community-product'),
        ]
        
        for title, link, descr, member_type in resources_l2_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l2_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        quiz_l2_1, _ = Quiz.objects.get_or_create(
            name='PM Level 2 - Roadmapping',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l2-roadmap'}
        )
        quiz_l2_2, _ = Quiz.objects.get_or_create(
            name='PM Level 2 - Analytics & Metrics',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l2-analytics'}
        )
        quiz_l2_3, _ = Quiz.objects.get_or_create(
            name='PM Level 2 - User Research',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l2-research'}
        )
        
        self._create_quiz_questions(quiz_l2_1, [
            ('Create a 6-month product roadmap outline for a SaaS product.', 'essay', 'community-product'),
            ('How do you communicate roadmap changes to stakeholders?', 'essay', 'community-product'),
        ])
        
        self._create_quiz_questions(quiz_l2_2, [
            ('Define North Star Metric and explain how to choose one for a product.', 'essay', 'community-product'),
            ('Design an A/B test for a checkout flow improvement.', 'essay', 'community-product'),
        ])
        
        self._create_quiz_questions(quiz_l2_3, [
            ('Describe when to use qualitative vs quantitative research methods.', 'essay', 'community-product'),
            ('How do you validate a product hypothesis before building?', 'essay', 'community-product'),
        ])
        
        cert_level_2, _ = CertificationLevel.objects.get_or_create(
            name='Product Manager Level 2',
            defaults={
                'level_type': 'intermediate',
                'track': 'product_manager',
                'description': 'Practitioner level for roadmapping, analytics, and user research.',
                'requirements': 'Complete 8 resources, pass 3 quizzes with 75%+, submit 2 documents.',
                'skills': 'Roadmapping, Analytics, OKRs, User Research, A/B Testing',
                'badge_color': '#7C3AED',
                'min_quiz_score': 75,
                'created_by': admin_user,
            }
        )
        cert_level_2.required_quizzes.set([quiz_l2_1, quiz_l2_2, quiz_l2_3])
        
        comm_level_2, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=2,
            defaults={
                'name': 'Product Manager Level 2 - Practitioner',
                'description': 'Master roadmapping, analytics, and user research.',
                'required_resources_count': 8,
                'required_quizzes_count': 3,
                'required_projects_count': 2,
                'min_quiz_score': 75,
                'certification_level': cert_level_2,
                'badge_color': '#7C3AED',
                'min_reviewer_level': 2,
            }
        )
        comm_level_2.resources.set(l2_resources)
        comm_level_2.quizzes.set([quiz_l2_1, quiz_l2_2, quiz_l2_3])
        
        self._create_project_placeholder(comm_level_2,
            'Product Roadmap',
            'Create a comprehensive 6-month product roadmap with OKRs and success metrics.',
            'document'
        )
        self._create_project_placeholder(comm_level_2,
            'User Research Report',
            'Conduct and document user research for a feature, including methodology and findings.',
            'document'
        )
        
        self.stdout.write(f'    ✓ Level 2 certification created')
        
        # ============ LEVEL 3: Senior ============
        self.stdout.write('  Level 3 - Senior:')
        
        l3_resources = []
        resources_l3_data = [
            ('RAD Process - Leadership & Scaling', 'https://buildly.io/rad-leadership', 'Leading RAD Process at scale.', 'community-product'),
            ('Product Strategy', 'https://www.reforge.com/blog/product-strategy', 'Developing product strategy.', 'community-product'),
            ('Market Analysis', 'https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/enduring-ideas-the-strategic-sweet-spot', 'Strategic market analysis.', 'community-product'),
            ('Product-Led Growth', 'https://www.productled.org/', 'PLG strategies and implementation.', 'community-product'),
            ('Team Leadership for PMs', 'https://www.svpg.com/empowered-product-teams/', 'Marty Cagan\'s empowered teams.', 'community-product'),
            ('Platform Strategy', 'https://hbr.org/2016/04/pipelines-platforms-and-the-new-rules-of-strategy', 'Platform business strategy.', 'community-product'),
            ('Product Vision & Mission', 'https://www.productplan.com/learn/product-vision/', 'Crafting product vision.', 'community-product'),
            ('Stakeholder Management at Scale', 'https://www.productboard.com/blog/stakeholder-management/', 'Managing stakeholders at scale.', 'community-product'),
            ('Cross-Functional Leadership', 'https://hbr.org/2015/06/cross-silo-leadership', 'Leading cross-functional teams.', 'community-product'),
            ('PM Career Ladders', 'https://www.levels.fyi/blog/product-manager-career-ladders.html', 'Product management career progression.', 'community-product'),
        ]
        
        for title, link, descr, member_type in resources_l3_data:
            resource, created = Resource.objects.get_or_create(
                title=title,
                defaults={'link': link, 'descr': descr, 'team_member_type': member_type}
            )
            l3_resources.append(resource)
            self.stdout.write(f'    ✓ Resource: {title}')
        
        quiz_l3_1, _ = Quiz.objects.get_or_create(
            name='PM Level 3 - Product Strategy',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l3-strategy'}
        )
        quiz_l3_2, _ = Quiz.objects.get_or_create(
            name='PM Level 3 - Market Analysis',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l3-market'}
        )
        quiz_l3_3, _ = Quiz.objects.get_or_create(
            name='PM Level 3 - Leadership',
            defaults={'owner': admin_user, 'available_date': date.today(), 'url': 'https://collab.buildly.io/quiz/pm-l3-leadership'}
        )
        
        self._create_quiz_questions(quiz_l3_1, [
            ('Develop a 3-year product strategy for entering a new market.', 'essay', 'community-product'),
            ('How do you balance platform vs product decisions?', 'essay', 'community-product'),
        ])
        
        self._create_quiz_questions(quiz_l3_2, [
            ('Conduct a competitive analysis for a product in a crowded market.', 'essay', 'community-product'),
            ('How do you identify and validate new market opportunities?', 'essay', 'community-product'),
        ])
        
        self._create_quiz_questions(quiz_l3_3, [
            ('How would you mentor a junior PM struggling with stakeholder management?', 'essay', 'community-product'),
            ('Describe your approach to leading a cross-functional product team.', 'essay', 'community-product'),
        ])
        
        cert_level_3, _ = CertificationLevel.objects.get_or_create(
            name='Product Manager Level 3 (Senior)',
            defaults={
                'level_type': 'senior',
                'track': 'product_manager',
                'description': 'Senior level for product strategy, market analysis, and leadership.',
                'requirements': 'Complete 10 resources, pass 3 quizzes with 80%+, submit 2 strategic documents.',
                'skills': 'Product Strategy, Market Analysis, PLG, Leadership, Platform Strategy',
                'badge_color': '#6D28D9',
                'min_quiz_score': 80,
                'created_by': admin_user,
            }
        )
        cert_level_3.required_quizzes.set([quiz_l3_1, quiz_l3_2, quiz_l3_3])
        
        comm_level_3, _ = CommunityCertificationLevel.objects.get_or_create(
            track=track,
            level=3,
            defaults={
                'name': 'Product Manager Level 3 - Senior',
                'description': 'Master product strategy, market analysis, and lead product teams.',
                'required_resources_count': 10,
                'required_quizzes_count': 3,
                'required_projects_count': 2,
                'min_quiz_score': 80,
                'certification_level': cert_level_3,
                'badge_color': '#6D28D9',
                'min_reviewer_level': 3,
            }
        )
        comm_level_3.resources.set(l3_resources)
        comm_level_3.quizzes.set([quiz_l3_1, quiz_l3_2, quiz_l3_3])
        
        self._create_project_placeholder(comm_level_3,
            'Product Strategy Document',
            'Create a comprehensive product strategy including market analysis, competitive positioning, and 3-year roadmap.',
            'document'
        )
        self._create_project_placeholder(comm_level_3,
            'Mentorship Documentation',
            'Document your mentorship of a junior PM including growth areas, feedback, and outcomes.',
            'document'
        )
        
        self.stdout.write(f'    ✓ Level 3 certification created')

    def setup_initial_reviewers(self):
        """Set up initial certified reviewers - Greg (L3), Radhika (L3), David (L2)"""
        self.stdout.write('\n👥 Setting up initial reviewers...')
        
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # Find or note the reviewers
        reviewers_config = [
            {'name': 'Greg Lind', 'first': 'Greg', 'last': 'Lind', 'level': 3, 'tracks': ['frontend', 'backend', 'product']},
            {'name': 'Radhika Patel', 'first': 'Radhika', 'last': 'Patel', 'level': 3, 'tracks': ['frontend', 'backend', 'product']},
            {'name': 'David Green', 'first': 'David', 'last': 'Green', 'level': 2, 'tracks': ['frontend', 'backend']},
        ]
        
        for config in reviewers_config:
            # Try to find the TeamMember
            try:
                developer = TeamMember.objects.filter(
                    first_name__iexact=config['first'],
                    last_name__iexact=config['last']
                ).first()
                
                if developer:
                    reviewer, created = CertifiedReviewer.objects.update_or_create(
                        developer=developer,
                        defaults={
                            'reviewer_level': config['level'],
                            'can_review_frontend': 'frontend' in config['tracks'],
                            'can_review_backend': 'backend' in config['tracks'],
                            'can_review_product': 'product' in config['tracks'],
                            'is_active': True,
                            'approved_by': admin_user,
                            'notes': f"Initial Level {config['level']} reviewer",
                        }
                    )
                    status = 'Created' if created else 'Updated'
                    self.stdout.write(f'  ✓ {status} reviewer: {config["name"]} (Level {config["level"]})')
                    
                    # Create public profile for reviewer
                    profile, _ = DeveloperPublicProfile.objects.get_or_create(
                        developer=developer,
                        defaults={
                            'is_public': True,
                            'headline': f'Senior Developer & Certified Reviewer',
                        }
                    )
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ TeamMember not found for {config["name"]}. '
                        f'Please create manually or ensure they register.'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error setting up {config["name"]}: {e}'))

    def _create_quiz_questions(self, quiz, questions_data):
        """Helper to create quiz questions"""
        for question_text, q_type, member_type in questions_data:
            QuizQuestion.objects.get_or_create(
                quiz=quiz,
                question=question_text,
                defaults={
                    'question_type': q_type,
                    'team_member_type': member_type,
                }
            )

    def _create_project_placeholder(self, cert_level, name, description, project_type):
        """Helper to create project placeholders"""
        project, created = CertificationProject.objects.get_or_create(
            certification_level=cert_level,
            name=name,
            defaults={
                'description': description,
                'project_type': project_type,
                'requirements_checklist': '[]',
                'max_score': 100,
                'passing_score': 70,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(f'    ✓ Project: {name}')
