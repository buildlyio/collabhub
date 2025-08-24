from django.contrib.auth.models import User
from onboarding.models import Quiz, QuizQuestion, TEAM_MEMBER_TYPES
from datetime import date

def create_quizzes():
    """Create quizzes and questions for different developer types"""
    
    # Get or create a default user for quiz ownership
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@buildly.io',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Frontend Developer Quiz
    frontend_quiz, created = Quiz.objects.get_or_create(
        name='Frontend Developer Certification',
        defaults={
            'owner': admin_user,
            'available_date': date.today(),
            'url': 'https://collab.buildly.io/quiz/frontend-certification'
        }
    )
    
    if created:
        print("Created Frontend Developer Quiz")
        
        frontend_questions = [
            {
                'question': 'What are the key principles of responsive web design, and how do you implement them in a Buildly application?',
                'question_type': 'essay'
            },
            {
                'question': 'Explain the difference between server-side rendering (SSR) and client-side rendering (CSR). When would you use each approach with Buildly?',
                'question_type': 'essay'
            },
            {
                'question': 'How do you integrate a React frontend with Buildly Core backend services? Describe the authentication flow and API communication.',
                'question_type': 'essay'
            },
            {
                'question': 'What testing strategies would you implement for a frontend application in the Buildly ecosystem? Include unit, integration, and E2E testing.',
                'question_type': 'essay'
            },
            {
                'question': 'Describe how you would optimize a frontend application for performance, including bundle size, loading times, and user experience.',
                'question_type': 'essay'
            }
        ]
        
        for q_data in frontend_questions:
            QuizQuestion.objects.create(
                team_member_type='buildly-hire-frontend',
                quiz=frontend_quiz,
                question=q_data['question'],
                question_type=q_data['question_type']
            )
    
    # Backend Developer Quiz
    backend_quiz, created = Quiz.objects.get_or_create(
        name='Backend Developer Certification',
        defaults={
            'owner': admin_user,
            'available_date': date.today(),
            'url': 'https://collab.buildly.io/quiz/backend-certification'
        }
    )
    
    if created:
        print("Created Backend Developer Quiz")
        
        backend_questions = [
            {
                'question': 'Explain the microservices architecture pattern and how Buildly Core implements it. What are the benefits and challenges?',
                'question_type': 'essay'
            },
            {
                'question': 'How do you design a RESTful API following best practices? Include considerations for versioning, authentication, and error handling.',
                'question_type': 'essay'
            },
            {
                'question': 'Describe the database migration process in Django. How would you handle schema changes in a production environment?',
                'question_type': 'essay'
            },
            {
                'question': 'What security considerations are important when developing backend services? How does Buildly Core address these concerns?',
                'question_type': 'essay'
            },
            {
                'question': 'Explain how you would implement caching, logging, and monitoring in a Buildly microservice for production deployment.',
                'question_type': 'essay'
            }
        ]
        
        for q_data in backend_questions:
            QuizQuestion.objects.create(
                team_member_type='buildly-hire-backend',
                quiz=backend_quiz,
                question=q_data['question'],
                question_type=q_data['question_type']
            )
    
    # AI Developer Quiz
    ai_quiz, created = Quiz.objects.get_or_create(
        name='AI Developer Certification',
        defaults={
            'owner': admin_user,
            'available_date': date.today(),
            'url': 'https://collab.buildly.io/quiz/ai-certification'
        }
    )
    
    if created:
        print("Created AI Developer Quiz")
        
        ai_questions = [
            {
                'question': 'What are the key principles of ethical AI development? How do you ensure fairness and transparency in AI applications?',
                'question_type': 'essay'
            },
            {
                'question': 'Explain the process of integrating a machine learning model into a Buildly microservice. Include deployment and monitoring considerations.',
                'question_type': 'essay'
            },
            {
                'question': 'How do you handle data privacy and security when working with AI models that process personal information?',
                'question_type': 'essay'
            },
            {
                'question': 'Describe the BabbleBeaver framework and how it facilitates ethical AI agent development. What are its key features?',
                'question_type': 'essay'
            },
            {
                'question': 'What strategies would you use to evaluate and improve the performance of an AI model in production?',
                'question_type': 'essay'
            }
        ]
        
        for q_data in ai_questions:
            QuizQuestion.objects.create(
                team_member_type='buildly-hire-ai',
                quiz=ai_quiz,
                question=q_data['question'],
                question_type=q_data['question_type']
            )

    # General Developer Quiz
    general_quiz, created = Quiz.objects.get_or_create(
        name='Buildly Platform General Knowledge',
        defaults={
            'owner': admin_user,
            'available_date': date.today(),
            'url': 'https://collab.buildly.io/quiz/general-certification'
        }
    )
    
    if created:
        print("Created General Developer Quiz")
        
        general_questions = [
            {
                'question': 'Explain the Radical Therapy development methodology. How does it apply to software development and team collaboration?',
                'question_type': 'essay'
            },
            {
                'question': 'Describe the Buildly platform ecosystem, including Labs, Core, and the various tools and services available.',
                'question_type': 'essay'
            },
            {
                'question': 'What are the best practices for contributing to open-source projects? How do you follow the Buildly contribution guidelines?',
                'question_type': 'essay'
            },
            {
                'question': 'How do you set up a development environment for Buildly projects? Include Docker, Git workflows, and IDE configuration.',
                'question_type': 'essay'
            }
        ]
        
        for q_data in general_questions:
            QuizQuestion.objects.create(
                team_member_type='all',
                quiz=general_quiz,
                question=q_data['question'],
                question_type=q_data['question_type']
            )

    print("Quiz creation completed!")

# Run the function
create_quizzes()
