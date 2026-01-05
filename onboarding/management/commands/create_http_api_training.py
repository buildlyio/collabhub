# onboarding/management/commands/create_http_api_training.py

from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from onboarding.models import Resource, Quiz, QuizQuestion


class Command(BaseCommand):
    help = "Create HTTP API training resources and quiz from Concrete Engine presentations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--owner-username",
            type=str,
            default="admin",
            help="Username of the Quiz owner (defaults to 'admin').",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        owner_username = options["owner_username"]

        try:
            owner = User.objects.get(username=owner_username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User '{owner_username}' not found."))
            return

        # ========== RESOURCES ==========
        resources_data = [
            {
                "title": "Software Engineering Fundamentals",
                "link": "https://concreteengine.github.io/presentations/data-mine-wk2/",
                "descr": (
                    "Introduction to software engineering principles: Design (stakeholders, workflows, failure branches), "
                    "Build (programming, research, stakeholder check-ins), Test (write tests, run tests, ensure coverage), "
                    "and Deploy (request review via pull request). Covers the full development lifecycle."
                ),
                "team_member_type": "all",
            },
            {
                "title": "Developing HTTP APIs with ExpressJS",
                "link": "https://concreteengine.github.io/presentations/http-express/",
                "descr": (
                    "Learn HTTP fundamentals and how to build APIs with ExpressJS. Covers HTTP request/response cycle, "
                    "HTTP methods (GET, POST, PUT, PATCH, DELETE), status codes (200, 302, 400, 404, 500), "
                    "and working with ExpressJS request/response objects."
                ),
                "team_member_type": "all",
            },
            {
                "title": "Developing HTTP APIs with Flask",
                "link": "https://concreteengine.github.io/presentations/http-flask/",
                "descr": (
                    "Learn HTTP fundamentals and how to build APIs with Python Flask. Covers HTTP request/response cycle, "
                    "Flask setup, route handlers (@app.route), sessions, form handling, GET/POST methods, "
                    "and Flask request/response objects."
                ),
                "team_member_type": "all",
            },
            {
                "title": "Concrete Engine x Data Mine Introduction",
                "link": "https://concreteengine.github.io/presentations/data-mine-wk1/",
                "descr": (
                    "Introduction to the Concrete Engine and Data Mine partnership at Purdue University. "
                    "Overview of the program and expectations for Fall 2025."
                ),
                "team_member_type": "all",
            },
        ]

        created_resources = []
        for data in resources_data:
            resource, created = Resource.objects.get_or_create(
                title=data["title"],
                team_member_type=data["team_member_type"],
                defaults={
                    "link": data["link"],
                    "descr": data["descr"],
                }
            )
            created_resources.append(resource)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created Resource: {data['title']}"))
            else:
                self.stdout.write(f"  Resource exists: {data['title']}")

        # ========== QUIZ ==========
        quiz, quiz_created = Quiz.objects.get_or_create(
            name="HTTP APIs & Software Engineering",
            owner=owner,
            defaults={
                "available_date": date.today(),
                "url": "https://collab.buildly.io/quizzes/http-api-training",
            },
        )

        if quiz_created:
            self.stdout.write(self.style.SUCCESS(f"\n✓ Created Quiz: {quiz.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"\n  Quiz exists: {quiz.name}"))

        # Link resources to the quiz
        for resource in created_resources:
            quiz.resources.add(resource)
        self.stdout.write(f"  Linked {len(created_resources)} resources to quiz")

        # ========== QUESTIONS ==========
        questions = [
            # HTTP Fundamentals
            {
                "text": (
                    "What does HTTP stand for?\n"
                    "A. Hyper Text Transfer Protocol\n"
                    "B. High Transfer Text Protocol\n"
                    "C. Hyper Text Transmission Protocol\n"
                    "D. Home Text Transfer Protocol"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "Which HTTP method is typically used to retrieve data from a server?\n"
                    "A. POST\n"
                    "B. PUT\n"
                    "C. GET\n"
                    "D. DELETE"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "What HTTP status code indicates a successful response?\n"
                    "A. 404\n"
                    "B. 500\n"
                    "C. 302\n"
                    "D. 200"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "What HTTP status code indicates 'Not Found'?\n"
                    "A. 200\n"
                    "B. 404\n"
                    "C. 500\n"
                    "D. 302"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "Which HTTP method is used to submit data to be processed (e.g., form submission)?\n"
                    "A. GET\n"
                    "B. DELETE\n"
                    "C. POST\n"
                    "D. PATCH"
                ),
                "type": "multiple_choice",
            },
            # Flask specific
            {
                "text": (
                    "In Flask, which decorator is used to define a route handler?\n"
                    "A. @flask.handler\n"
                    "B. @app.route\n"
                    "C. @route.handler\n"
                    "D. @http.endpoint"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "In Flask, how do you access form data from a POST request?\n"
                    "A. request.body['field']\n"
                    "B. request.form['field']\n"
                    "C. request.data['field']\n"
                    "D. request.post['field']"
                ),
                "type": "multiple_choice",
            },
            # ExpressJS specific
            {
                "text": (
                    "In ExpressJS, how do you access the request path?\n"
                    "A. req.url\n"
                    "B. req.path\n"
                    "C. req.route\n"
                    "D. req.endpoint"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "In ExpressJS, how do you set the HTTP status code on a response?\n"
                    "A. res.code(404)\n"
                    "B. res.status(404)\n"
                    "C. res.setStatus(404)\n"
                    "D. res.httpCode(404)"
                ),
                "type": "multiple_choice",
            },
            # Software Engineering
            {
                "text": (
                    "According to Google's definition, software engineering can be thought of as:\n"
                    "A. Writing code as fast as possible\n"
                    "B. Programming integrated over time\n"
                    "C. Only testing and debugging\n"
                    "D. Documentation only"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "What are the four main phases of the software engineering process covered in the training?\n"
                    "A. Code, Compile, Run, Debug\n"
                    "B. Design, Build, Test, Deploy\n"
                    "C. Plan, Write, Execute, Ship\n"
                    "D. Analyze, Develop, Integrate, Release"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "In the software engineering workflow, what is the purpose of the 'Design' phase?\n"
                    "A. Writing all the code\n"
                    "B. Identify stakeholders, determine workflows, enumerate failure branches\n"
                    "C. Running automated tests\n"
                    "D. Deploying to production"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "What is the recommended way to request a code review in the deployment process?\n"
                    "A. Send an email to the team\n"
                    "B. Create a Pull Request\n"
                    "C. Post in Slack\n"
                    "D. Schedule a meeting"
                ),
                "type": "multiple_choice",
            },
            # Essay questions
            {
                "text": (
                    "Explain the difference between a GET and POST request. "
                    "When would you use each one? Provide examples."
                ),
                "type": "essay",
            },
            {
                "text": (
                    "Describe the HTTP request/response cycle. What components make up an HTTP request "
                    "and what components make up an HTTP response?"
                ),
                "type": "essay",
            },
            {
                "text": (
                    "Compare Flask (Python) and ExpressJS (Node.js) for building HTTP APIs. "
                    "What are the similarities and differences in how they handle routes and requests?"
                ),
                "type": "essay",
            },
            {
                "text": (
                    "Explain the software engineering lifecycle (Design → Build → Test → Deploy). "
                    "Why is each phase important and what activities happen in each?"
                ),
                "type": "essay",
            },
        ]

        questions_created = 0
        for q_data in questions:
            question, created = QuizQuestion.objects.get_or_create(
                quiz=quiz,
                question=q_data["text"],
                defaults={
                    "team_member_type": "all",
                    "question_type": q_data["type"],
                }
            )
            if created:
                questions_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Complete: {len(created_resources)} resources, 1 quiz, {questions_created} new questions"
        ))
        self.stdout.write(f"\nQuiz URL: /onboarding/quiz/{quiz.id}/")
