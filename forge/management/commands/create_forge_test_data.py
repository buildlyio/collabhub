from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from forge.models import ForgeApp, Purchase, Entitlement, UserProfile
import uuid


class Command(BaseCommand):
    help = 'Create sample Forge apps and data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of test users to create'
        )
        parser.add_argument(
            '--apps',
            type=int,
            default=10,
            help='Number of test apps to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data first'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            # Delete test apps (those with specific naming pattern)
            ForgeApp.objects.filter(slug__startswith='test-').delete()
            # Delete test users (those with specific naming pattern)
            User.objects.filter(username__startswith='testuser').delete()
            self.stdout.write(self.style.SUCCESS('Test data cleared'))
        
        # Create test users
        self.stdout.write(f"Creating {options['users']} test users...")
        test_users = []
        
        for i in range(options['users']):
            username = f'testuser{i+1}'
            email = f'testuser{i+1}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test',
                    'last_name': f'User {i+1}',
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('testpassword')
                user.save()
                
                # Create user profile (some as labs customers)
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'is_labs_customer': i % 3 == 0}  # Every 3rd user is labs customer
                )
                
                test_users.append(user)
                self.stdout.write(f'Created user: {username}')
            else:
                test_users.append(user)
                self.stdout.write(f'User exists: {username}')
        
        # Sample app data
        sample_apps = [
            {
                'slug': 'test-buildly-dashboard',
                'name': 'Buildly Dashboard',
                'summary': 'Advanced analytics dashboard for Buildly applications',
                'price_cents': 2999,
                'categories': ['analytics', 'dashboard'],
                'targets': ['docker', 'k8s'],
                'license_type': 'mit'
            },
            {
                'slug': 'test-api-gateway',
                'name': 'API Gateway Pro',
                'summary': 'Enterprise API gateway with rate limiting and monitoring',
                'price_cents': 4999,
                'categories': ['infrastructure', 'api'],
                'targets': ['docker', 'k8s'],
                'license_type': 'apache2'
            },
            {
                'slug': 'test-user-management',
                'name': 'User Management Suite',
                'summary': 'Complete user authentication and authorization system',
                'price_cents': 1999,
                'categories': ['authentication', 'security'],
                'targets': ['docker', 'web-embed'],
                'license_type': 'mit'
            },
            {
                'slug': 'test-notification-service',
                'name': 'Notification Service',
                'summary': 'Multi-channel notification system with templates',
                'price_cents': 1499,
                'categories': ['communication', 'service'],
                'targets': ['docker', 'k8s'],
                'license_type': 'mit'
            },
            {
                'slug': 'test-data-viz',
                'name': 'Data Visualization Toolkit',
                'summary': 'Interactive charts and graphs for data presentation',
                'price_cents': 3499,
                'categories': ['visualization', 'analytics'],
                'targets': ['web-embed', 'github-pages'],
                'license_type': 'mit'
            },
            {
                'slug': 'test-file-manager',
                'name': 'Cloud File Manager',
                'summary': 'Secure file upload, storage, and sharing system',
                'price_cents': 2499,
                'categories': ['storage', 'utility'],
                'targets': ['docker', 'desktop'],
                'license_type': 'gpl3'
            },
            {
                'slug': 'test-workflow-engine',
                'name': 'Workflow Engine',
                'summary': 'Visual workflow builder and automation engine',
                'price_cents': 5999,
                'categories': ['automation', 'workflow'],
                'targets': ['docker', 'k8s'],
                'license_type': 'commercial'
            },
            {
                'slug': 'test-payment-processor',
                'name': 'Payment Processor',
                'summary': 'Multi-gateway payment processing with fraud detection',
                'price_cents': 7999,
                'categories': ['payment', 'fintech'],
                'targets': ['docker', 'k8s'],
                'license_type': 'commercial'
            },
            {
                'slug': 'test-cms-lite',
                'name': 'CMS Lite',
                'summary': 'Lightweight content management system',
                'price_cents': 999,
                'categories': ['cms', 'content'],
                'targets': ['github-pages', 'web-embed'],
                'license_type': 'mit'
            },
            {
                'slug': 'test-monitoring-stack',
                'name': 'Monitoring Stack',
                'summary': 'Complete application monitoring and alerting solution',
                'price_cents': 4499,
                'categories': ['monitoring', 'devops'],
                'targets': ['docker', 'k8s'],
                'license_type': 'apache2'
            }
        ]
        
        # Create test apps
        self.stdout.write(f"Creating {min(options['apps'], len(sample_apps))} test apps...")
        created_apps = []
        
        for i, app_data in enumerate(sample_apps[:options['apps']]):
            app, created = ForgeApp.objects.get_or_create(
                slug=app_data['slug'],
                defaults={
                    'name': app_data['name'],
                    'summary': app_data['summary'],
                    'price_cents': app_data['price_cents'],
                    'repo_url': f"https://github.com/buildly-marketplace/{app_data['slug'][5:]}",  # Remove 'test-' prefix
                    'repo_owner': 'buildly-marketplace',
                    'repo_name': app_data['slug'][5:],  # Remove 'test-' prefix
                    'license_type': app_data['license_type'],
                    'categories': app_data['categories'],
                    'targets': app_data['targets'],
                    'is_published': True,
                    'logo_url': f'https://via.placeholder.com/200x200?text={app_data["name"].replace(" ", "+")}',
                    'screenshots': [
                        'https://via.placeholder.com/800x600?text=Screenshot+1',
                        'https://via.placeholder.com/800x600?text=Screenshot+2'
                    ]
                }
            )
            
            if created:
                created_apps.append(app)
                self.stdout.write(f'Created app: {app.name} (${app.price_cents/100:.2f})')
            else:
                created_apps.append(app)
                self.stdout.write(f'App exists: {app.name}')
        
        # Create some test purchases and entitlements
        if test_users and created_apps:
            self.stdout.write('Creating test purchases...')
            
            # Each user purchases 1-3 random apps
            import random
            for user in test_users[:3]:  # Only first 3 users get purchases
                user_profile = UserProfile.objects.get(user=user)
                num_purchases = random.randint(1, 3)
                
                # Select random apps for this user
                apps_to_purchase = random.sample(created_apps, min(num_purchases, len(created_apps)))
                
                for app in apps_to_purchase:
                    # Calculate price with potential discount
                    price_cents = app.price_cents
                    discount_applied = False
                    
                    if user_profile.is_labs_customer:
                        price_cents = price_cents // 2
                        discount_applied = True
                    
                    # Create purchase
                    purchase = Purchase.objects.create(
                        user=user,
                        forge_app=app,
                        amount_cents=price_cents,
                        discount_applied=discount_applied,
                        status='completed',
                        stripe_payment_intent_id=f'pi_test_{uuid.uuid4().hex[:16]}'
                    )
                    
                    # Create entitlement
                    Entitlement.objects.get_or_create(
                        user=user,
                        forge_app=app,
                        defaults={'purchase': purchase}
                    )
                    
                    discount_str = ' (50% Labs discount)' if discount_applied else ''
                    self.stdout.write(f'  {user.username} purchased {app.name} for ${price_cents/100:.2f}{discount_str}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Test data creation complete!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'  Users: {len(test_users)}')
        self.stdout.write(f'  Apps: {len(created_apps)}')
        self.stdout.write(f'  Purchases: {Purchase.objects.filter(user__in=test_users).count()}')
        self.stdout.write(f'  Entitlements: {Entitlement.objects.filter(user__in=test_users).count()}')
        
        self.stdout.write('\nTest credentials:')
        for user in test_users:
            profile = UserProfile.objects.get(user=user)
            labs_status = ' (Labs Customer)' if profile.is_labs_customer else ''
            self.stdout.write(f'  {user.username}:testpassword{labs_status}')
        
        self.stdout.write('\nAPI endpoints to test:')
        self.stdout.write('  GET /forge/api/apps/ - List published apps')
        self.stdout.write('  GET /forge/api/apps/test-buildly-dashboard/ - App details')
        self.stdout.write('  POST /forge/api/purchases/create_checkout/ - Create purchase (authenticated)')
        self.stdout.write('  GET /forge/api/entitlements/ - User entitlements (authenticated)')