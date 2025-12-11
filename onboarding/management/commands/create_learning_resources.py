# onboarding/management/commands/create_learning_resources.py

from django.core.management.base import BaseCommand
from onboarding.models import Resource, TEAM_MEMBER_TYPES


class Command(BaseCommand):
    help = "Create learning resources for all topics covered in the Developer Assessment"

    def handle(self, *args, **options):
        # Topics covered in the assessment (extracted from quiz questions)
        topics = {
            # Core Programming & Development
            "production_code": {
                "title": "Writing Production-Quality Code",
                "link": "https://www.freecodecamp.org/news/how-to-write-production-ready-code/",
                "descr": "Learn best practices for writing clean, maintainable, production-ready code including error handling, logging, testing, and documentation."
            },
            "debugging": {
                "title": "Debugging Techniques and Tools",
                "link": "https://developers.google.com/web/tools/chrome-devtools/javascript",
                "descr": "Master systematic debugging approaches: reproduce issues, isolate problems, inspect state, implement fixes, and verify solutions."
            },
            
            # Version Control
            "git": {
                "title": "Git Version Control Mastery",
                "link": "https://learngitbranching.js.org/",
                "descr": "Complete guide to Git: branching strategies, pull requests, code reviews, merge conflicts, and team workflows."
            },
            
            # Architecture & Design
            "microservices": {
                "title": "Microservice Architecture Fundamentals",
                "link": "https://microservices.io/patterns/microservices.html",
                "descr": "Understanding microservice principles, service communication, data management, and distributed system design patterns."
            },
            "api_design": {
                "title": "RESTful API Design Best Practices",
                "link": "https://restfulapi.net/",
                "descr": "Learn API design principles including REST, GraphQL, HTTP methods, request/response patterns, versioning, and error handling."
            },
            "api_gateways": {
                "title": "API Gateways and Reverse Proxies",
                "link": "https://www.nginx.com/learn/api-gateway/",
                "descr": "Understanding API gateways for routing, authentication, rate limiting, and request/response transformation."
            },
            
            # DevOps & Deployment
            "deployment": {
                "title": "Application Deployment Strategies",
                "link": "https://www.digitalocean.com/community/tutorials/an-introduction-to-continuous-integration-delivery-and-deployment",
                "descr": "Learn deployment processes, cloud platforms, environment management, and deployment best practices."
            },
            "cicd": {
                "title": "CI/CD Pipeline Design and Implementation",
                "link": "https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment",
                "descr": "Master continuous integration and deployment: automated testing, build pipelines, deployment automation, and rollback strategies."
            },
            
            # Team Collaboration
            "agile": {
                "title": "Agile Development Methodologies",
                "link": "https://www.atlassian.com/agile",
                "descr": "Understanding Agile, Scrum, Kanban: sprints, standups, retrospectives, and iterative development processes."
            },
            "code_review": {
                "title": "Effective Code Review Practices",
                "link": "https://google.github.io/eng-practices/review/",
                "descr": "Learn how to give and receive constructive code reviews, set review standards, and improve code quality through peer review."
            },
            "task_breakdown": {
                "title": "Breaking Down Features into Tasks",
                "link": "https://www.atlassian.com/agile/project-management/epics-stories-themes",
                "descr": "Learn to decompose features into tasks, estimate work, identify dependencies, and coordinate across teams."
            },
            
            # Modern Development Tools
            "ai_assisted": {
                "title": "AI-Assisted Development Workflows",
                "link": "https://github.com/features/copilot",
                "descr": "Leveraging AI tools like GitHub Copilot, ChatGPT, and Labs workflows for coding, debugging, documentation, and planning."
            },
            
            # Professional Skills
            "codebase_orientation": {
                "title": "Navigating Unfamiliar Codebases",
                "link": "https://www.freecodecamp.org/news/how-to-read-code/",
                "descr": "Strategies for quickly understanding new codebases: reading code, tracing execution, finding entry points, and identifying patterns."
            },
            "requirements_gathering": {
                "title": "Requirements Gathering and Clarification",
                "link": "https://www.atlassian.com/agile/product-management/requirements",
                "descr": "How to handle unclear requirements, ask effective questions, document assumptions, and align with stakeholders."
            },
            "problem_solving": {
                "title": "Technical Problem-Solving Frameworks",
                "link": "https://www.freecodecamp.org/news/how-to-think-like-a-programmer-lessons-in-problem-solving-d1d8bf1de7d2/",
                "descr": "Systematic approaches to solving technical challenges: problem decomposition, research, prototyping, and iterative refinement."
            },
        }
        
        created_count = 0
        updated_count = 0
        
        for topic_key, data in topics.items():
            resource, created = Resource.objects.get_or_create(
                team_member_type='all',
                title=data['title'],
                defaults={
                    'link': data['link'],
                    'descr': data['descr'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {data['title']}"))
            else:
                # Update if link or description changed
                updated = False
                if resource.link != data['link']:
                    resource.link = data['link']
                    updated = True
                if resource.descr != data['descr']:
                    resource.descr = data['descr']
                    updated = True
                    
                if updated:
                    resource.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"↻ Updated: {data['title']}"))
                else:
                    self.stdout.write(f"  Exists: {data['title']}")
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Finished: {created_count} created, {updated_count} updated, {len(topics)} total resources"
        ))
