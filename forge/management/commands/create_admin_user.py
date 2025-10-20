from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from forge.models import UserProfile
import os
import secrets
import string


class Command(BaseCommand):
    help = 'Create or update admin superuser for Forge marketplace management'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@buildly.io',
            help='Admin email (default: admin@buildly.io)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Admin password (will generate secure password if not provided)'
        )
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Skip creation if admin user already exists'
        )
        parser.add_argument(
            '--labs-customer',
            action='store_true',
            help='Mark admin as labs customer for testing discounts'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Check if user already exists
        try:
            admin_user = User.objects.get(username=username)
            if options['skip_if_exists']:
                self.stdout.write(
                    self.style.WARNING(f'Admin user "{username}" already exists, skipping...')
                )
                return
            else:
                self.stdout.write(f'Updating existing admin user "{username}"...')
                created = False
        except User.DoesNotExist:
            admin_user = None
            created = True
        
        # Generate secure password if not provided
        if not password:
            # Generate a secure 16-character password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(alphabet) for i in range(16))
        
        # Create or update admin user
        if created:
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            admin_user.first_name = 'Buildly'
            admin_user.last_name = 'Administrator'
            admin_user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created admin superuser: {username}')
            )
        else:
            # Update existing user
            admin_user.email = email
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.set_password(password)
            admin_user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Updated admin superuser: {username}')
            )
        
        # Create or update user profile for Forge
        user_profile, profile_created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'is_labs_customer': options['labs_customer']}
        )
        
        if not profile_created and options['labs_customer']:
            user_profile.is_labs_customer = True
            user_profile.save()
        
        profile_status = 'Labs Customer' if user_profile.is_labs_customer else 'Regular User'
        self.stdout.write(f'📊 Profile status: {profile_status}')
        
        # Show credentials
        self.stdout.write('\n' + '='*50)
        self.stdout.write('🔐 ADMIN CREDENTIALS')
        self.stdout.write('='*50)
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Email: {email}')
        self.stdout.write('='*50)
        
        # Show access URLs
        self.stdout.write('\n🌐 Admin Access:')
        self.stdout.write('  Django Admin: /admin/')
        self.stdout.write('  Forge Apps: /admin/forge/forgeapp/')
        self.stdout.write('  Purchases: /admin/forge/purchase/')
        self.stdout.write('  Validations: /admin/forge/repovalidation/')
        
        # Security reminder
        self.stdout.write('\n⚠️  SECURITY NOTES:')
        self.stdout.write('  • Store these credentials securely')
        self.stdout.write('  • Change the password in production')
        self.stdout.write('  • Consider using environment variables')
        self.stdout.write('  • Enable 2FA if available')
        
        # Environment variable suggestion
        if not options['password']:
            self.stdout.write('\n💡 To set password via environment variable:')
            self.stdout.write(f'  export DJANGO_ADMIN_PASSWORD="{password}"')
            self.stdout.write('  python manage.py create_admin_user --password "$DJANGO_ADMIN_PASSWORD"')
        
        return admin_user