# onboarding/management/commands/create_training_quizzes.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from onboarding.models import Resource, Quiz, QuizQuestion


class Command(BaseCommand):
    help = "Create Docker, Ansible, and Express training resources and quizzes"

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

        # Try to find the specified user
        owner = User.objects.filter(username=owner_username).first()
        
        # If not found, try to find any superuser
        if not owner:
            owner = User.objects.filter(is_superuser=True).first()
            if owner:
                self.stdout.write(self.style.WARNING(
                    f"User '{owner_username}' not found. Using superuser '{owner.username}' instead."
                ))
        
        # If still no owner, list available users and exit
        if not owner:
            available_users = User.objects.values_list('username', flat=True)[:10]
            self.stderr.write(self.style.ERROR(f"User '{owner_username}' not found."))
            self.stderr.write(self.style.ERROR(f"Available users: {list(available_users)}"))
            return

        # ==================== DOCKER TRAINING ====================
        self._create_docker_training(owner)
        
        # ==================== EXPRESS TRAINING ====================
        self._create_express_training(owner)
        
        # ==================== ANSIBLE TRAINING ====================
        self._create_ansible_training(owner)

        self.stdout.write(self.style.SUCCESS("\n✅ All training quizzes created successfully!"))

    def _create_docker_training(self, owner):
        self.stdout.write("\n📦 Creating Docker Fundamentals Training...")
        
        # Create Resource
        resource, created = Resource.objects.update_or_create(
            title="Docker Fundamentals for Customer Projects",
            defaults={
                "link": "https://www.youtube.com/watch?v=3c-iBn73dDE",
                "descr": (
                    "Learn Docker fundamentals including containers, images, Dockerfiles, environment variables, "
                    "and Docker Compose. At Buildly, Docker is the delivery contract - if a service runs in Docker, "
                    "it can be reviewed, tested, and deployed consistently for customers."
                ),
                "team_member_type": "all",
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} resource: {resource.title}")

        # Create Quiz
        quiz, created = Quiz.objects.update_or_create(
            name="Docker Fundamentals Quiz",
            defaults={
                "description": (
                    "Test your understanding of Docker concepts including containers, images, Dockerfiles, "
                    "environment variables, and Docker Compose for customer project delivery."
                ),
                "owner": owner,
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} quiz: {quiz.name}")

        # Docker Quiz Questions
        docker_questions = [
            # Multiple Choice Questions
            {
                "question": "Docker primarily helps Buildly by:",
                "question_type": "multiple_choice",
                "choices": "A. Making apps faster\nB. Ensuring consistent environments\nC. Replacing cloud providers\nD. Reducing code complexity",
                "correct_answer": "B",
                "order": 1,
            },
            {
                "question": "Where should secrets (API keys, passwords) be stored in a Docker setup?",
                "question_type": "multiple_choice",
                "choices": "A. In the Dockerfile\nB. In source code\nC. In environment variables\nD. In the README file",
                "correct_answer": "C",
                "order": 2,
            },
            {
                "question": "Docker Compose is best used for:",
                "question_type": "multiple_choice",
                "choices": "A. CI pipelines only\nB. Local multi-service environments\nC. Manual server setup\nD. Database backups",
                "correct_answer": "B",
                "order": 3,
            },
            {
                "question": "What is the difference between a Docker image and a container?",
                "question_type": "multiple_choice",
                "choices": "A. They are the same thing\nB. Image is a blueprint, container is a running instance\nC. Container is a blueprint, image is a running instance\nD. Images are for production, containers are for development",
                "correct_answer": "B",
                "order": 4,
            },
            {
                "question": "What file defines how a Docker image is built?",
                "question_type": "multiple_choice",
                "choices": "A. docker-compose.yml\nB. package.json\nC. Dockerfile\nD. requirements.txt",
                "correct_answer": "C",
                "order": 5,
            },
            {
                "question": "Why is Docker important for reducing customer risk at Buildly?",
                "question_type": "multiple_choice",
                "choices": "A. It makes code run faster\nB. It eliminates all bugs\nC. It ensures consistent environments across development, testing, and production\nD. It automatically writes tests",
                "correct_answer": "C",
                "order": 6,
            },
            {
                "question": "What command starts all services defined in a docker-compose.yml file?",
                "question_type": "multiple_choice",
                "choices": "A. docker run all\nB. docker-compose up\nC. docker start services\nD. docker build compose",
                "correct_answer": "B",
                "order": 7,
            },
            {
                "question": "What is the purpose of a .dockerignore file?",
                "question_type": "multiple_choice",
                "choices": "A. To list Docker commands to ignore\nB. To exclude files from being copied into the Docker image\nC. To ignore Docker errors\nD. To skip certain containers",
                "correct_answer": "B",
                "order": 8,
            },
            # Essay Questions
            {
                "question": "Explain in your own words why Docker is described as 'the delivery contract' at Buildly. What does this mean for how you should approach containerizing customer applications?",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 9,
            },
            {
                "question": "Describe a scenario where hardcoding secrets in a Dockerfile could cause problems for a customer. How would you properly handle configuration and secrets instead?",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 10,
            },
            {
                "question": "You're asked to Dockerize a Node.js application that connects to a PostgreSQL database. Describe the steps you would take and what files you would create.",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 11,
            },
        ]

        self._create_questions(quiz, docker_questions)
        self.stdout.write(f"  Created {len(docker_questions)} questions for Docker quiz")

    def _create_express_training(self, owner):
        self.stdout.write("\n🚀 Creating Node.js & Express Training...")
        
        # Create Resource
        resource, created = Resource.objects.update_or_create(
            title="Node.js & Express for Customer APIs",
            defaults={
                "link": "https://www.youtube.com/watch?v=L72fhGm1tfE",
                "descr": (
                    "Learn to build reliable APIs with Node.js and Express. Covers the Node.js runtime, event loop, "
                    "Express framework, routing, middleware, and error handling. Focus on creating predictable, "
                    "transparent APIs that customers can trust."
                ),
                "team_member_type": "all",
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} resource: {resource.title}")

        # Create Quiz
        quiz, created = Quiz.objects.update_or_create(
            name="Node.js & Express API Quiz",
            defaults={
                "description": (
                    "Test your understanding of Node.js runtime, Express framework, middleware patterns, "
                    "routing, and professional error handling for customer-facing APIs."
                ),
                "owner": owner,
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} quiz: {quiz.name}")

        # Express Quiz Questions
        express_questions = [
            # Multiple Choice Questions
            {
                "question": "Express is:",
                "question_type": "multiple_choice",
                "choices": "A. A database\nB. A web framework\nC. A container runtime\nD. A testing library",
                "correct_answer": "B",
                "order": 1,
            },
            {
                "question": "Middleware in Express can run:",
                "question_type": "multiple_choice",
                "choices": "A. Only before routes\nB. Only after responses\nC. Before and/or after routes\nD. Only during errors",
                "correct_answer": "C",
                "order": 2,
            },
            {
                "question": "An HTTP 500 error indicates:",
                "question_type": "multiple_choice",
                "choices": "A. Client error (bad request)\nB. Server error\nC. Authentication required\nD. Resource not found",
                "correct_answer": "B",
                "order": 3,
            },
            {
                "question": "What HTTP status code should be returned when a resource is successfully created?",
                "question_type": "multiple_choice",
                "choices": "A. 200 OK\nB. 201 Created\nC. 204 No Content\nD. 302 Found",
                "correct_answer": "B",
                "order": 4,
            },
            {
                "question": "In Node.js, blocking code is problematic because:",
                "question_type": "multiple_choice",
                "choices": "A. It uses too much memory\nB. It affects all users since Node.js is single-threaded\nC. It crashes the server\nD. It's not valid JavaScript",
                "correct_answer": "B",
                "order": 5,
            },
            {
                "question": "What is the correct HTTP method for updating an existing resource?",
                "question_type": "multiple_choice",
                "choices": "A. GET\nB. POST\nC. PUT or PATCH\nD. DELETE",
                "correct_answer": "C",
                "order": 6,
            },
            {
                "question": "Why should stack traces NOT be sent to customers in error responses?",
                "question_type": "multiple_choice",
                "choices": "A. They're too long\nB. They expose internal implementation details and potential security vulnerabilities\nC. They slow down responses\nD. Customers can't read them",
                "correct_answer": "B",
                "order": 7,
            },
            {
                "question": "What does 'async/await' help with in Node.js?",
                "question_type": "multiple_choice",
                "choices": "A. Making code run faster\nB. Writing cleaner asynchronous code that's easier to read and debug\nC. Connecting to databases\nD. Handling HTTP requests",
                "correct_answer": "B",
                "order": 8,
            },
            {
                "question": "In Express, what is the purpose of app.use()?",
                "question_type": "multiple_choice",
                "choices": "A. To define database connections\nB. To register middleware that runs for all or specific routes\nC. To start the server\nD. To define environment variables",
                "correct_answer": "B",
                "order": 9,
            },
            # Essay Questions
            {
                "question": "Explain the Express middleware pattern. How does the order of middleware registration affect request processing? Give an example of when order matters.",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 10,
            },
            {
                "question": "A customer reports that their API sometimes returns 'undefined' in JSON responses. What are the most likely causes, and how would you debug and fix this issue?",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 11,
            },
            {
                "question": "Describe how you would implement centralized error handling in an Express application. What should error responses look like for a customer-facing API?",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 12,
            },
            {
                "question": "You're building a REST API for a customer. List the HTTP methods you would use for CRUD operations and explain what status codes each operation should return for success and common failure cases.",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 13,
            },
        ]

        self._create_questions(quiz, express_questions)
        self.stdout.write(f"  Created {len(express_questions)} questions for Express quiz")

    def _create_ansible_training(self, owner):
        self.stdout.write("\n⚙️ Creating Ansible Training...")
        
        # Create Resource
        resource, created = Resource.objects.update_or_create(
            title="Ansible for Reliable Delivery",
            defaults={
                "link": "https://www.youtube.com/watch?v=1id6ERvfozo",
                "descr": (
                    "Learn Ansible for infrastructure automation. Covers Infrastructure as Code concepts, "
                    "inventory management, playbooks, idempotency, and variables. At Buildly, automation "
                    "is professionalism - manual server changes don't scale and increase customer risk."
                ),
                "team_member_type": "all",
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} resource: {resource.title}")

        # Create Quiz
        quiz, created = Quiz.objects.update_or_create(
            name="Ansible Fundamentals Quiz",
            defaults={
                "description": (
                    "Test your understanding of Ansible concepts including Infrastructure as Code, "
                    "inventory files, playbooks, idempotency, and using variables for reliable infrastructure delivery."
                ),
                "owner": owner,
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} quiz: {quiz.name}")

        # Ansible Quiz Questions
        ansible_questions = [
            # Multiple Choice Questions
            {
                "question": "Ansible is best used for:",
                "question_type": "multiple_choice",
                "choices": "A. Writing application logic\nB. Automated, repeatable infrastructure changes\nC. Manual server configuration\nD. Frontend development",
                "correct_answer": "B",
                "order": 1,
            },
            {
                "question": "Idempotent means:",
                "question_type": "multiple_choice",
                "choices": "A. Runs only once\nB. Safe to run multiple times with the same result\nC. Runs very quickly\nD. Requires no configuration",
                "correct_answer": "B",
                "order": 2,
            },
            {
                "question": "Ansible inventory files define:",
                "question_type": "multiple_choice",
                "choices": "A. Application code\nB. Target hosts to be managed\nC. Secrets and passwords\nD. Docker containers",
                "correct_answer": "B",
                "order": 3,
            },
            {
                "question": "What format are Ansible playbooks written in?",
                "question_type": "multiple_choice",
                "choices": "A. JSON\nB. XML\nC. YAML\nD. Python",
                "correct_answer": "C",
                "order": 4,
            },
            {
                "question": "Why is 'Infrastructure as Code' important for customer delivery?",
                "question_type": "multiple_choice",
                "choices": "A. It's faster to type\nB. Changes are reviewable, repeatable, and history is preserved\nC. It eliminates all bugs\nD. Customers prefer code over documentation",
                "correct_answer": "B",
                "order": 5,
            },
            {
                "question": "What happens when you run an idempotent Ansible playbook twice?",
                "question_type": "multiple_choice",
                "choices": "A. It fails on the second run\nB. It duplicates all changes\nC. It only makes changes if needed, resulting in the same end state\nD. It deletes previous changes",
                "correct_answer": "C",
                "order": 6,
            },
            {
                "question": "Ansible connects to managed hosts using:",
                "question_type": "multiple_choice",
                "choices": "A. HTTP\nB. SSH (by default)\nC. FTP\nD. Docker",
                "correct_answer": "B",
                "order": 7,
            },
            {
                "question": "What is the benefit of using variables in Ansible playbooks?",
                "question_type": "multiple_choice",
                "choices": "A. They make playbooks longer\nB. They enable reuse across different environments and reduce duplication\nC. They're required by Ansible\nD. They improve security",
                "correct_answer": "B",
                "order": 8,
            },
            {
                "question": "An Ansible 'task' represents:",
                "question_type": "multiple_choice",
                "choices": "A. A complete playbook\nB. A single action to be performed on managed hosts\nC. A group of servers\nD. A variable definition",
                "correct_answer": "B",
                "order": 9,
            },
            # Essay Questions
            {
                "question": "Explain why 'manual server changes increase customer risk' as stated in the Buildly philosophy. How does Ansible address this risk?",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 10,
            },
            {
                "question": "Describe idempotency in the context of Ansible and why it's critical for customer trust. Give an example of an idempotent vs non-idempotent operation.",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 11,
            },
            {
                "question": "You need to deploy the same application to development, staging, and production environments. How would you structure your Ansible playbooks and use variables to handle environment-specific differences?",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 12,
            },
            {
                "question": "A customer asks you to set up a new server manually 'just this once' because it's urgent. How would you respond, and what would you recommend instead?",
                "question_type": "essay",
                "choices": "",
                "correct_answer": "",
                "order": 13,
            },
        ]

        self._create_questions(quiz, ansible_questions)
        self.stdout.write(f"  Created {len(ansible_questions)} questions for Ansible quiz")

    def _create_questions(self, quiz, questions_data):
        """Create or update quiz questions."""
        for q_data in questions_data:
            QuizQuestion.objects.update_or_create(
                quiz=quiz,
                question=q_data["question"],
                defaults={
                    "question_type": q_data["question_type"],
                    "choices": q_data["choices"],
                    "correct_answer": q_data["correct_answer"],
                    "order": q_data["order"],
                }
            )
