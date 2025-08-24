#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Add the project directory to Python path
sys.path.append('/Users/greglind/Projects/buildly/collabhub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.production')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from onboarding.models import Resource, Quiz, QuizQuestion, TEAM_MEMBER_TYPES

def create_resources():
    """Create comprehensive resources for different developer types"""
    
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
            'descr': 'Comprehensive guide to marketing technology products and developer tools effectively.'
        },
        {
            'title': 'Content Marketing for Open Source',
            'link': 'https://docs.buildly.io/marketing/content-strategy',
            'descr': 'Creating engaging content that builds developer communities around open-source projects.'
        },
        {
            'title': 'Community Building and Engagement',
            'link': 'https://buildly.io/community',
            'descr': 'Strategies for building and nurturing developer communities, from Discord to GitHub.'
        },
        {
            'title': 'SEO for Developer Products',
            'link': 'https://buildly.io/blog/developer-seo',
            'descr': 'Technical SEO strategies for improving visibility of developer tools and documentation.'
        }
    ]
    
    # Product Management Resources
    product_resources = [
        {
            'title': 'Product Management for Developer Tools',
            'link': 'https://docs.buildly.io/product/developer-tools',
            'descr': 'Product management strategies specific to developer tools and technical products.'
        },
        {
            'title': 'Agile Development with Buildly',
            'link': 'https://buildly.io/blog/agile-development',
            'descr': 'Implementing agile methodologies in technical product development and open-source projects.'
        },
        {
            'title': 'User Research for Technical Products',
            'link': 'https://docs.buildly.io/product/user-research',
            'descr': 'Conducting effective user research with developers and technical stakeholders.'
        },
        {
            'title': 'Roadmap Planning and Prioritization',
            'link': 'https://buildly.io/blog/product-roadmap',
            'descr': 'Creating and managing product roadmaps for technical products and platform development.'
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
    
    print("Creating resources...")
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
                print(f"Created: {resource.title} for {team_type}")
    
    print(f"Total resources created: {created_count}")

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
                'question': 'Explain the difference between server-side rendering (SSR) and client-side rendering (CSR). When would you use each approach?',
                'question_type': 'essay'
            },
            {
                'question': 'How do you integrate a React frontend with Buildly Core backend services? Describe the authentication flow.',
                'question_type': 'essay'
            },
            {
                'question': 'What testing strategies would you implement for a frontend application in the Buildly ecosystem?',
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
                'question': 'Describe the BabbleBeaver framework and how it facilitates ethical AI agent development.',
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

def main():
    print("Starting content creation...")
    create_resources()
    create_quizzes()
    print("Content creation completed!")

if __name__ == '__main__':
    main()
