from django.contrib.auth.models import User
from onboarding.models import Resource, Quiz, QuizQuestion, TEAM_MEMBER_TYPES
from datetime import date

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

# Run the function
create_resources()
