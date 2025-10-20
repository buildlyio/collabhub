#!/usr/bin/env python
"""
Production initialization script for Buildly CollabHub onboarding content.
This script creates comprehensive onboarding resources and quizzes for all developer types.
"""
import os
import sys
import django
from datetime import date

# Add the project directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

# Setup Django - use production settings by default, but allow override
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'mysite.settings.production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup()

from django.contrib.auth.models import User
from onboarding.models import Resource, Quiz, QuizQuestion

def init_onboarding_content():
    """Initialize comprehensive onboarding content for production environment"""
    
    print("🚀 Initializing Buildly CollabHub onboarding content...")
    
    # Frontend Developer Resources
    frontend_resources = [
        {
            'title': 'Buildly Frontend Development Guide',
            'link': 'https://docs.buildly.io/frontend',
            'descr': 'Complete guide to frontend development with Buildly framework including React, Vue.js, and Angular integrations.'
        },
        {
            'title': 'Buildly UI Components Library',
            'link': 'https://github.com/buildlyio/buildly-ui-angular',
            'descr': 'Open-source Angular UI components library for rapid frontend development with Buildly ecosystem.'
        },
        {
            'title': 'Frontend Testing Best Practices',
            'link': 'https://buildly.io/blog/frontend-testing',
            'descr': 'Learn testing strategies for frontend applications including unit tests, integration tests, and E2E testing.'
        },
        {
            'title': 'React Integration with Buildly Core',
            'link': 'https://github.com/buildlyio/buildly-react-template',
            'descr': 'Template and documentation for integrating React applications with Buildly Core backend services.'
        },
        {
            'title': 'Responsive Design Guidelines',
            'link': 'https://docs.buildly.io/design/responsive',
            'descr': 'Mobile-first design principles and responsive web design patterns for Buildly applications.'
        }
    ]
    
    # Backend Developer Resources  
    backend_resources = [
        {
            'title': 'Buildly Core Framework Documentation',
            'link': 'https://github.com/buildlyio/buildly-core',
            'descr': 'Complete documentation for Buildly Core - the microservices framework powering scalable applications.'
        },
        {
            'title': 'API Development with Django REST',
            'link': 'https://docs.buildly.io/backend/api-development',
            'descr': 'Learn to build robust REST APIs using Django REST framework within the Buildly ecosystem.'
        },
        {
            'title': 'Microservices Architecture Guide',
            'link': 'https://buildly.io/blog/microservices-architecture',
            'descr': 'Understanding microservices patterns, service discovery, and inter-service communication in Buildly.'
        },
        {
            'title': 'Database Design and Migrations',
            'link': 'https://docs.buildly.io/backend/database',
            'descr': 'Best practices for database schema design, migrations, and data modeling in Buildly applications.'
        },
        {
            'title': 'Authentication and Authorization',
            'link': 'https://github.com/buildlyio/buildly-core/tree/main/core/auth',
            'descr': 'Implementing secure authentication and role-based authorization in Buildly microservices.'
        },
        {
            'title': 'Docker and Containerization',
            'link': 'https://docs.buildly.io/deployment/docker',
            'descr': 'Containerizing Buildly applications with Docker for development and production environments.'
        }
    ]
    
    # AI/ML Developer Resources
    ai_resources = [
        {
            'title': 'BabbleBeaver AI Framework',
            'link': 'https://github.com/open-build/BabbleBeaver',
            'descr': 'Lightweight open-source AI modules for connecting and testing AI agents in ethical AI applications.'
        },
        {
            'title': 'Machine Learning Pipeline Integration',
            'link': 'https://docs.buildly.io/ai/ml-pipelines',
            'descr': 'Integrating ML models and pipelines into Buildly microservices architecture.'
        },
        {
            'title': 'AI Ethics and Responsible Development',
            'link': 'https://buildly.io/blog/ethical-ai-development',
            'descr': 'Guidelines for developing ethical AI applications with transparency and fairness principles.'
        },
        {
            'title': 'Natural Language Processing with Buildly',
            'link': 'https://github.com/buildlyio/buildly-nlp-service',
            'descr': 'NLP service template for building language processing capabilities into Buildly applications.'
        },
        {
            'title': 'AI Model Deployment and Monitoring',
            'link': 'https://docs.buildly.io/ai/model-deployment',
            'descr': 'Best practices for deploying and monitoring AI models in production Buildly environments.'
        }
    ]
    
    # Marketing Resources
    marketing_resources = [
        {
            'title': 'Digital Marketing Strategy for Tech Products',
            'link': 'https://buildly.io/blog/tech-marketing-strategy',
            'descr': 'Comprehensive guide to marketing technology products and developer tools effectively in the modern digital landscape.'
        },
        {
            'title': 'Content Marketing for Open Source Projects',
            'link': 'https://docs.buildly.io/marketing/content-strategy',
            'descr': 'Creating engaging content that builds developer communities around open-source projects and technical products.'
        },
        {
            'title': 'Community Building and Developer Engagement',
            'link': 'https://buildly.io/community/building',
            'descr': 'Strategies for building and nurturing developer communities, from Discord to GitHub, Slack to Stack Overflow.'
        },
        {
            'title': 'SEO for Developer Products and Documentation',
            'link': 'https://buildly.io/blog/developer-seo',
            'descr': 'Technical SEO strategies for improving visibility of developer tools, API documentation, and technical content.'
        },
        {
            'title': 'Developer Relations and Community Management',
            'link': 'https://buildly.io/devrel/best-practices',
            'descr': 'Best practices for developer relations, community management, and building authentic relationships with technical audiences.'
        }
    ]
    
    # Product Management Resources
    product_resources = [
        {
            'title': 'Product Management for Developer Tools',
            'link': 'https://docs.buildly.io/product/developer-tools',
            'descr': 'Product management strategies specific to developer tools, APIs, and technical products in the Buildly ecosystem.'
        },
        {
            'title': 'Agile Development with Buildly Framework',
            'link': 'https://buildly.io/blog/agile-development',
            'descr': 'Implementing agile methodologies in technical product development and open-source project management.'
        },
        {
            'title': 'User Research for Technical Products',
            'link': 'https://docs.buildly.io/product/user-research',
            'descr': 'Conducting effective user research with developers and technical stakeholders, including survey design and interviews.'
        },
        {
            'title': 'Roadmap Planning and Feature Prioritization',
            'link': 'https://buildly.io/blog/product-roadmap',
            'descr': 'Creating and managing product roadmaps for technical products and platform development with stakeholder input.'
        }
    ]
    
    # General/Everyone Resources
    general_resources = [
        {
            'title': 'Buildly Platform Overview',
            'link': 'https://buildly.io/platform',
            'descr': 'Complete overview of the Buildly platform, its components, and how they work together.'
        },
        {
            'title': 'Getting Started with Buildly Labs',
            'link': 'https://labs.buildly.io/getting-started',
            'descr': 'Step-by-step guide to getting started with Buildly Labs for project development and collaboration.'
        },
        {
            'title': 'Open Source Contribution Guidelines',
            'link': 'https://github.com/buildlyio/buildly-core/blob/main/CONTRIBUTING.md',
            'descr': 'Guidelines for contributing to Buildly open-source projects, including code standards and PR process.'
        },
        {
            'title': 'Radical Therapy Development Methodology',
            'link': 'https://www.radicaltherapy.dev',
            'descr': 'Revolutionary development methodology focusing on healing and sustainable software development practices.'
        },
        {
            'title': 'Buildly Community Slack',
            'link': 'https://buildly.io/slack',
            'descr': 'Join the Buildly community Slack for real-time discussions, support, and collaboration.'
        },
        {
            'title': 'GitHub Workflows and Best Practices',
            'link': 'https://docs.buildly.io/development/github-workflows',
            'descr': 'Best practices for using GitHub in the Buildly ecosystem, including branching strategies and code review.'
        },
        {
            'title': 'Buildly Core Tutorial Series',
            'link': 'https://www.youtube.com/watch?v=buildly-core-intro',
            'descr': 'Complete video tutorial series introducing Buildly Core microservices framework and basic setup.'
        },
        {
            'title': 'Buildly Labs Platform Walkthrough',
            'link': 'https://www.youtube.com/watch?v=buildly-labs-tour',
            'descr': 'Complete walkthrough of the Buildly Labs platform, including project management and collaboration features.'
        }
    ]
    
    # Create resources for each team member type
    resource_mapping = {
        'buildly-hire-frontend': frontend_resources,
        'community-frontend': frontend_resources,
        'buildly-hire-backend': backend_resources, 
        'community-backend': backend_resources,
        'buildly-hire-ai': ai_resources,
        'community-ai': ai_resources,
        'buildly-hire-marketing': marketing_resources,
        'buildly-hire-marketing-intern': marketing_resources,
        'community-marketing-agency': marketing_resources,
        'buildly-hire-product': product_resources,
        'community-product': product_resources,
        'all': general_resources
    }
    
    print("📚 Creating onboarding resources...")
    created_count = 0
    
    for team_type, resources in resource_mapping.items():
        for resource_data in resources:
            resource, created = Resource.objects.get_or_create(
                team_member_type=team_type,
                title=resource_data['title'],
                defaults={
                    'link': resource_data['link'],
                    'descr': resource_data['descr']
                }
            )
            if created:
                created_count += 1
                print(f"  ✅ Created: {resource.title} for {team_type}")
    
    print(f"📊 Total resources created: {created_count}")
    
    # Create or get admin user for quiz ownership
    admin_user, user_created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@buildly.io',
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'Buildly',
            'last_name': 'Administrator'
        }
    )
    
    if user_created:
        print("👤 Created admin user for quiz ownership")
    
    print("🎯 Creating certification quizzes...")
    
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
        print("  ✅ Created Frontend Developer Quiz")
        frontend_questions = [
            "What are the key principles of responsive web design, and how do you implement them in a Buildly application?",
            "Explain the difference between server-side rendering (SSR) and client-side rendering (CSR). When would you use each approach with Buildly?",
            "How do you integrate a React frontend with Buildly Core backend services? Describe the authentication flow and API communication.",
            "What testing strategies would you implement for a frontend application in the Buildly ecosystem? Include unit, integration, and E2E testing.",
            "Describe how you would optimize a frontend application for performance, including bundle size, loading times, and user experience."
        ]
        
        for question in frontend_questions:
            QuizQuestion.objects.get_or_create(
                team_member_type='buildly-hire-frontend',
                quiz=frontend_quiz,
                question=question,
                defaults={'question_type': 'essay'}
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
        print("  ✅ Created Backend Developer Quiz")
        backend_questions = [
            "Explain the microservices architecture pattern and how Buildly Core implements it. What are the benefits and challenges?",
            "How do you design a RESTful API following best practices? Include considerations for versioning, authentication, and error handling.",
            "Describe the database migration process in Django. How would you handle schema changes in a production environment?",
            "What security considerations are important when developing backend services? How does Buildly Core address these concerns?",
            "Explain how you would implement caching, logging, and monitoring in a Buildly microservice for production deployment."
        ]
        
        for question in backend_questions:
            QuizQuestion.objects.get_or_create(
                team_member_type='buildly-hire-backend',
                quiz=backend_quiz,
                question=question,
                defaults={'question_type': 'essay'}
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
        print("  ✅ Created AI Developer Quiz")
        ai_questions = [
            "What are the key principles of ethical AI development? How do you ensure fairness and transparency in AI applications?",
            "Explain the process of integrating a machine learning model into a Buildly microservice. Include deployment and monitoring considerations.",
            "How do you handle data privacy and security when working with AI models that process personal information?",
            "Describe the BabbleBeaver framework and how it facilitates ethical AI agent development. What are its key features?",
            "What strategies would you use to evaluate and improve the performance of an AI model in production?"
        ]
        
        for question in ai_questions:
            QuizQuestion.objects.get_or_create(
                team_member_type='buildly-hire-ai',
                quiz=ai_quiz,
                question=question,
                defaults={'question_type': 'essay'}
            )
    
    # Marketing Quiz
    marketing_quiz, created = Quiz.objects.get_or_create(
        name='Marketing Professional Certification',
        defaults={
            'owner': admin_user,
            'available_date': date.today(),
            'url': 'https://collab.buildly.io/quiz/marketing-certification'
        }
    )
    
    if created:
        print("  ✅ Created Marketing Professional Quiz")
        marketing_questions = [
            "How do you develop a content marketing strategy for a technical product or open-source project? Include audience research and content planning.",
            "Describe effective strategies for building and engaging developer communities. Include both online and offline approaches.",
            "What are the key differences between marketing to developers versus marketing to traditional business audiences?",
            "How would you measure the success of a developer relations program? Include metrics and KPIs."
        ]
        
        for question in marketing_questions:
            QuizQuestion.objects.get_or_create(
                team_member_type='buildly-hire-marketing',
                quiz=marketing_quiz,
                question=question,
                defaults={'question_type': 'essay'}
            )
    
    # Product Management Quiz
    product_quiz, created = Quiz.objects.get_or_create(
        name='Product Manager Certification',
        defaults={
            'owner': admin_user,
            'available_date': date.today(),
            'url': 'https://collab.buildly.io/quiz/product-certification'
        }
    )
    
    if created:
        print("  ✅ Created Product Manager Quiz")
        product_questions = [
            "How do you conduct user research for developer tools and technical products? Include research methods and stakeholder interviews.",
            "Describe your approach to creating and maintaining a product roadmap for a technical platform like Buildly.",
            "What metrics would you use to measure the success of an API or developer platform? Explain your reasoning.",
            "How do you prioritize feature requests from both technical and non-technical stakeholders?"
        ]
        
        for question in product_questions:
            QuizQuestion.objects.get_or_create(
                team_member_type='buildly-hire-product',
                quiz=product_quiz,
                question=question,
                defaults={'question_type': 'essay'}
            )
    
    # General Quiz
    general_quiz, created = Quiz.objects.get_or_create(
        name='Buildly Platform General Knowledge',
        defaults={
            'owner': admin_user,
            'available_date': date.today(),
            'url': 'https://collab.buildly.io/quiz/general-certification'
        }
    )
    
    if created:
        print("  ✅ Created General Platform Quiz")
        general_questions = [
            "Explain the Radical Therapy development methodology. How does it apply to software development and team collaboration?",
            "Describe the Buildly platform ecosystem, including Labs, Core, and the various tools and services available.",
            "What are the best practices for contributing to open-source projects? How do you follow the Buildly contribution guidelines?",
            "How do you set up a development environment for Buildly projects? Include Docker, Git workflows, and IDE configuration."
        ]
        
        for question in general_questions:
            QuizQuestion.objects.get_or_create(
                team_member_type='all',
                quiz=general_quiz,
                question=question,
                defaults={'question_type': 'essay'}
            )
    
    # Final summary
    total_resources = Resource.objects.count()
    total_quizzes = Quiz.objects.count()
    total_questions = QuizQuestion.objects.count()
    
    print("🎉 Buildly CollabHub onboarding content initialization complete!")
    print(f"📊 Database summary:")
    print(f"  - Resources: {total_resources}")
    print(f"  - Certification Quizzes: {total_quizzes}")
    print(f"  - Quiz Questions: {total_questions}")
    print("✅ Ready for production use!")

if __name__ == '__main__':
    try:
        init_onboarding_content()
    except Exception as e:
        print(f"❌ Error initializing onboarding content: {e}")
        sys.exit(1)