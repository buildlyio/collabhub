# onboarding/management/commands/create_developer_level_quiz.py

from datetime import date

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from onboarding.models import Quiz, QuizQuestion, TEAM_MEMBER_TYPES


class Command(BaseCommand):
    help = "Create the Developer Level Assessment quiz and questions for team_member_type='all'."

    def add_arguments(self, parser):
        parser.add_argument(
            "--owner-username",
            type=str,
            default="admin",
            help="Username of the Quiz owner (defaults to 'admin').",
        )
        parser.add_argument(
            "--quiz-url",
            type=str,
            default="https://collab.buildly.io/quizzes/developer-level-assessment",
            help="Public URL for the quiz.",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        owner_username = options["owner_username"]
        quiz_url = options["quiz_url"]

        try:
            owner = User.objects.get(username=owner_username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User '{owner_username}' not found."))
            return

        quiz, created = Quiz.objects.get_or_create(
            name="Developer Level Assessment",
            owner=owner,
            defaults={
                "available_date": date.today(),
                "url": quiz_url,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Quiz: {quiz.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Quiz already exists: {quiz.name}"))

        # We'll use the generic 'all' type
        team_member_type_value = "all"

        # Make sure 'all' exists in TEAM_MEMBER_TYPES
        valid_types = [x[0] for x in TEAM_MEMBER_TYPES]
        if team_member_type_value not in valid_types:
            self.stderr.write(self.style.ERROR(
                f"'all' is not a valid team_member_type. Available types: {valid_types}"
            ))
            return

        # Question definitions
        questions = [
            # Section A
            {
                "text": (
                    "How comfortable are you writing production code in your primary programming language?\n"
                    "A. I can write small scripts or simple programs, usually by following examples\n"
                    "B. I can implement features if someone provides guidance or a clear specification\n"
                    "C. I can design and implement features independently in a production codebase\n"
                    "D. I design or review application-level architecture and make technical decisions for others"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How do you typically approach debugging an issue in an application or service?\n"
                    "A. I mostly try things until it works (print/console logs, guessing)\n"
                    "B. I use logs or a debugger to narrow down where the issue is happening\n"
                    "C. I follow a structured approach (reproduce → isolate → inspect → fix → test)\n"
                    "D. I can debug issues that involve multiple services, environments, or systems working together"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "Which best describes your understanding and use of Git?\n"
                    "A. I can clone a repo, make changes, and push commits\n"
                    "B. I can create branches and open basic pull requests (PRs)\n"
                    "C. I understand branching strategies, code reviews, and resolving merge conflicts\n"
                    "D. I help define the repo workflow, enforce standards, and mentor others on Git"
                ),
                "type": "multiple_choice",
            },

            # Section B
            {
                "text": (
                    "How familiar are you with microservice architecture concepts?\n"
                    "A. I am not familiar with microservices\n"
                    "B. I know the basic idea (multiple services, APIs, and databases)\n"
                    "C. I have worked on or maintained one or more microservices\n"
                    "D. I have designed or refactored systems using microservice principles"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How familiar are you with deploying applications?\n"
                    "A. I have only run applications locally on my machine\n"
                    "B. I have deployed an application with help from someone else or following a guide\n"
                    "C. I have used CI/CD pipelines or deployment scripts to deploy to a cloud environment\n"
                    "D. I manage or design deployment processes across multiple environments (dev, test, staging, prod)"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How comfortable are you with API design (REST, GraphQL, or similar)?\n"
                    "A. I can call APIs if I have documentation or examples\n"
                    "B. I understand endpoints, HTTP methods, and basic request/response payloads\n"
                    "C. I can design and implement API endpoints, including validation and error handling\n"
                    "D. I design or review API contracts across services and think about versioning and compatibility"
                ),
                "type": "multiple_choice",
            },

            # Section C
            {
                "text": (
                    "Have you worked in a team using a structured development process (Agile, Kanban, RAD-style, etc.)?\n"
                    "A. I have not really worked on a team project yet\n"
                    "B. I have worked on a team, but the process was mostly informal\n"
                    "C. I have worked in a team using Agile/Scrum/Kanban or similar structured processes\n"
                    "D. I have helped shape or improve the team's process (for example, introducing better standups, retros, or RAD-like flow)"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How often have you participated in code reviews?\n"
                    "A. Rarely or never\n"
                    "B. I regularly have my code reviewed by others\n"
                    "C. I regularly review other people's code and leave constructive feedback\n"
                    "D. I set standards for reviews and mentor others during the review process"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How comfortable are you breaking down a feature into tasks or tickets?\n"
                    "A. I usually need someone else to break down the work for me\n"
                    "B. I can break down simple features into a few tasks when given clear requirements\n"
                    "C. I can break down complex features into tasks, estimate them, and identify dependencies\n"
                    "D. I lead decomposition for multi-service features and coordinate work across multiple people"
                ),
                "type": "multiple_choice",
            },

            # Section D
            {
                "text": (
                    "How familiar are you with API Gateways or reverse proxies (for example, Nginx, Kong, custom gateway services)?\n"
                    "A. I am not familiar with API gateways\n"
                    "B. I know conceptually that a gateway routes requests to different services\n"
                    "C. I have configured or extended an API gateway or reverse proxy\n"
                    "D. I have designed gateway routes, authentication flows, or request/response transformations"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How familiar are you with CI/CD pipelines for cloud-native applications?\n"
                    "A. I have never used a CI/CD pipeline\n"
                    "B. I have fixed simple pipeline issues or followed existing pipelines\n"
                    "C. I can create or modify CI/CD pipelines for services or applications\n"
                    "D. I design CI/CD workflows across multiple services/environments with tests, approvals, and rollbacks"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How often do you use AI-assisted tools (such as Buildly Labs-style workflows, GitHub Copilot, ChatGPT, etc.) in your development work?\n"
                    "A. I have not used AI tools for development\n"
                    "B. I occasionally use AI tools for code or documentation help\n"
                    "C. I regularly use AI for coding, debugging, or planning tasks\n"
                    "D. AI-assisted workflows are a core part of how I design, plan, and implement work"
                ),
                "type": "multiple_choice",
            },

            # Section E
            {
                "text": (
                    "How would you describe your overall experience level as a software developer?\n"
                    "A. Beginner / early junior\n"
                    "B. Intermediate / mid-level\n"
                    "C. Experienced / senior\n"
                    "D. Lead / architect / staff-level"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How confident are you working independently in a new or unfamiliar codebase?\n"
                    "A. Not very confident\n"
                    "B. Somewhat confident; I can move with guidance\n"
                    "C. Mostly confident; I can figure things out and ask for help when needed\n"
                    "D. Very confident; I can onboard myself and help others understand the system"
                ),
                "type": "multiple_choice",
            },
            {
                "text": (
                    "How many years of collaborative software development experience do you have "
                    "(school projects, internships, jobs, open source, etc.)?\n"
                    "A. Less than 1 year\n"
                    "B. 1–3 years\n"
                    "C. 3–7 years\n"
                    "D. More than 7 years"
                ),
                "type": "multiple_choice",
            },

            # Section F – Essays
            {
                "text": (
                    "Describe a recent technical problem you solved. What made it challenging, and how did you approach it?"
                ),
                "type": "essay",
            },
            {
                "text": (
                    "When you join a new codebase or project, what is your typical process to get oriented and become productive?"
                ),
                "type": "essay",
            },
            {
                "text": (
                    "If a product owner or stakeholder gives you unclear requirements, what do you do next?"
                ),
                "type": "essay",
            },
        ]

        created_count = 0
        for idx, q in enumerate(questions, start=1):
            qq, q_created = QuizQuestion.objects.get_or_create(
                quiz=quiz,
                team_member_type=team_member_type_value,
                question=q["text"],
                defaults={"question_type": q["type"]},
            )
            if q_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created question {idx}: {q['type']}"))
            else:
                # Optionally update type if changed
                if qq.question_type != q["type"]:
                    qq.question_type = q["type"]
                    qq.save(update_fields=["question_type"])
                    self.stdout.write(self.style.WARNING(f"Updated type for question {idx}"))

        self.stdout.write(self.style.SUCCESS(f"Finished. {created_count} questions created or updated."))
