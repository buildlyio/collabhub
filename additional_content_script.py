from django.contrib.auth.models import User
from onboarding.models import Resource, Quiz, QuizQuestion, TEAM_MEMBER_TYPES
from datetime import date

def create_additional_resources():
    """Create additional resources for marketing, product, and other roles"""
    
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
        },
        {
            'title': 'Social Media Strategy for Tech Companies',
            'link': 'https://buildly.io/marketing/social-media',
            'descr': 'Effective social media strategies for technical products, including LinkedIn, Twitter, and developer-focused platforms.'
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
        },
        {
            'title': 'API Product Management',
            'link': 'https://buildly.io/product/api-management',
            'descr': 'Specialized product management techniques for APIs, developer experience, and platform products.'
        },
        {
            'title': 'Technical Product Analytics',
            'link': 'https://docs.buildly.io/product/analytics',
            'descr': 'Analytics and metrics for technical products, including developer adoption, API usage, and product-market fit.'
        }
    ]
    
    # UI/UX Designer Resources
    design_resources = [
        {
            'title': 'Design Systems for Developer Tools',
            'link': 'https://buildly.io/design/design-systems',
            'descr': 'Creating consistent design systems for developer tools and technical interfaces in the Buildly ecosystem.'
        },
        {
            'title': 'User Experience for APIs and Documentation',
            'link': 'https://docs.buildly.io/design/api-ux',
            'descr': 'UX principles for designing developer-friendly APIs, documentation, and technical interfaces.'
        },
        {
            'title': 'Accessibility in Technical Products',
            'link': 'https://buildly.io/design/accessibility',
            'descr': 'Implementing accessibility best practices in developer tools and technical user interfaces.'
        },
        {
            'title': 'Prototyping for Developer Interfaces',
            'link': 'https://buildly.io/design/prototyping',
            'descr': 'Prototyping techniques and tools for developer-facing interfaces and technical products.'
        },
        {
            'title': 'Visual Design for Technical Documentation',
            'link': 'https://docs.buildly.io/design/documentation',
            'descr': 'Visual design principles for technical documentation, code examples, and developer resources.'
        }
    ]
    
    # Agency-specific Resources  
    agency_resources = [
        {
            'title': 'Client Management for Technical Projects',
            'link': 'https://buildly.io/agency/client-management',
            'descr': 'Best practices for managing clients in technical development projects and software agency work.'
        },
        {
            'title': 'Project Estimation and Scoping',
            'link': 'https://buildly.io/agency/project-scoping',
            'descr': 'Techniques for accurately estimating and scoping technical projects using Buildly framework.'
        },
        {
            'title': 'Quality Assurance for Agency Projects',
            'link': 'https://docs.buildly.io/agency/quality-assurance',
            'descr': 'QA processes and testing strategies for software agency projects using Buildly tools.'
        },
        {
            'title': 'Delivery and Deployment Best Practices',
            'link': 'https://buildly.io/agency/delivery',
            'descr': 'Best practices for delivering and deploying client projects using Buildly infrastructure.'
        }
    ]
    
    # YouTube Video Resources
    video_resources = [
        {
            'title': 'Buildly Core Tutorial Series - Getting Started',
            'link': 'https://www.youtube.com/watch?v=buildly-core-intro',
            'descr': 'Complete video tutorial series introducing Buildly Core microservices framework and basic setup.'
        },
        {
            'title': 'Frontend Development with Buildly - Live Coding',
            'link': 'https://www.youtube.com/watch?v=buildly-frontend-demo',
            'descr': 'Live coding session showing how to build a frontend application integrated with Buildly backend services.'
        },
        {
            'title': 'Deploying Buildly Applications with Docker',
            'link': 'https://www.youtube.com/watch?v=buildly-docker-deploy',
            'descr': 'Step-by-step video guide for containerizing and deploying Buildly applications using Docker and Kubernetes.'
        },
        {
            'title': 'AI Integration with BabbleBeaver Framework',
            'link': 'https://www.youtube.com/watch?v=babblebeaver-ai-demo',
            'descr': 'Demonstration of integrating AI capabilities using the BabbleBeaver framework for ethical AI development.'
        },
        {
            'title': 'Buildly Labs Platform Walkthrough',
            'link': 'https://www.youtube.com/watch?v=buildly-labs-tour',
            'descr': 'Complete walkthrough of the Buildly Labs platform, including project management and collaboration features.'
        }
    ]
    
    # Create resources for each team member type
    resource_mapping = {
        'buildly-hire-marketing': marketing_resources,
        'buildly-hire-marketing-intern': marketing_resources,
        'community-marketing-agency': marketing_resources,
        'buildly-hire-product': product_resources,
        'community-product': product_resources,
        'community-ui-designer': design_resources,
        'community-ux': design_resources,
        'community-software-agency': agency_resources,
        'community-design-agency': agency_resources,
        'all': video_resources  # Video resources for everyone
    }
    
    print("Creating additional resources...")
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
    
    print(f"Total additional resources created: {created_count}")

def create_additional_quizzes():
    """Create quizzes for marketing, product, and other roles"""
    
    # Get admin user
    admin_user = User.objects.get(username='admin')
    
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
        print("Created Marketing Professional Quiz")
        
        marketing_questions = [
            {
                'question': 'How do you develop a content marketing strategy for a technical product or open-source project? Include audience research and content planning.',
                'question_type': 'essay'
            },
            {
                'question': 'Describe effective strategies for building and engaging developer communities. Include both online and offline approaches.',
                'question_type': 'essay'
            },
            {
                'question': 'What are the key differences between marketing to developers versus marketing to traditional business audiences?',
                'question_type': 'essay'
            },
            {
                'question': 'How would you measure the success of a developer relations program? Include metrics and KPIs.',
                'question_type': 'essay'
            }
        ]
        
        for q_data in marketing_questions:
            QuizQuestion.objects.create(
                team_member_type='buildly-hire-marketing',
                quiz=marketing_quiz,
                question=q_data['question'],
                question_type=q_data['question_type']
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
        print("Created Product Manager Quiz")
        
        product_questions = [
            {
                'question': 'How do you conduct user research for developer tools and technical products? Include research methods and stakeholder interviews.',
                'question_type': 'essay'
            },
            {
                'question': 'Describe your approach to creating and maintaining a product roadmap for a technical platform like Buildly.',
                'question_type': 'essay'
            },
            {
                'question': 'What metrics would you use to measure the success of an API or developer platform? Explain your reasoning.',
                'question_type': 'essay'
            },
            {
                'question': 'How do you prioritize feature requests from both technical and non-technical stakeholders?',
                'question_type': 'essay'
            }
        ]
        
        for q_data in product_questions:
            QuizQuestion.objects.create(
                team_member_type='buildly-hire-product',
                quiz=product_quiz,
                question=q_data['question'],
                question_type=q_data['question_type']
            )

    print("Additional quiz creation completed!")

# Run the functions
create_additional_resources()
create_additional_quizzes()
