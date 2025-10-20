from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from onboarding.models import TeamMember
from forge.models import UserProfile


class Command(BaseCommand):
    help = 'Approve all pending TeamMembers and create missing profiles'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-approve',
            action='store_true',
            help='Automatically approve all existing TeamMembers'
        )
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Create TeamMember profiles for users who don\'t have one'
        )
        parser.add_argument(
            '--default-type',
            type=str,
            default='community-member-generic',
            help='Default team member type for missing profiles'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get stats
        total_users = User.objects.count()
        total_team_members = TeamMember.objects.count()
        unapproved_team_members = TeamMember.objects.filter(approved=False).count()
        users_without_team_member = User.objects.exclude(
            id__in=TeamMember.objects.values_list('user_id', flat=True)
        ).count()
        
        self.stdout.write('\n📊 Current Status:')
        self.stdout.write(f'  Total Users: {total_users}')
        self.stdout.write(f'  Total TeamMembers: {total_team_members}')
        self.stdout.write(f'  Unapproved TeamMembers: {unapproved_team_members}')
        self.stdout.write(f'  Users without TeamMember profile: {users_without_team_member}')
        
        approved_count = 0
        created_count = 0
        
        # Auto-approve existing TeamMembers
        if options['auto_approve']:
            self.stdout.write('\n🔓 Approving existing TeamMembers...')
            
            for team_member in TeamMember.objects.filter(approved=False):
                if not dry_run:
                    team_member.approved = True
                    team_member.save()
                
                self.stdout.write(f'  ✅ Approved: {team_member.first_name} {team_member.last_name} ({team_member.team_member_type})')
                approved_count += 1
        
        # Create missing TeamMember profiles
        if options['create_missing']:
            self.stdout.write(f'\n👤 Creating missing TeamMember profiles...')
            
            users_without_profile = User.objects.exclude(
                id__in=TeamMember.objects.values_list('user_id', flat=True)
            )
            
            for user in users_without_profile:
                if not dry_run:
                    team_member = TeamMember.objects.create(
                        user=user,
                        team_member_type=options['default_type'],
                        first_name=user.first_name or 'Unknown',
                        last_name=user.last_name or 'User',
                        email=user.email,
                        approved=True  # Auto-approve new profiles
                    )
                    
                    # Also create Forge profile
                    UserProfile.objects.get_or_create(
                        user=user,
                        defaults={'is_labs_customer': False}
                    )
                
                self.stdout.write(f'  ➕ Created profile: {user.username} ({user.email})')
                created_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write('DRY RUN SUMMARY (no changes made):')
        else:
            self.stdout.write('APPROVAL SUMMARY:')
        
        self.stdout.write(f'  TeamMembers approved: {approved_count}')
        self.stdout.write(f'  New profiles created: {created_count}')
        
        if not dry_run and (approved_count > 0 or created_count > 0):
            self.stdout.write(self.style.SUCCESS('✅ All users should now be able to access the dashboard!'))
        
        # Show final stats
        if not dry_run:
            final_approved = TeamMember.objects.filter(approved=True).count()
            final_total = TeamMember.objects.count()
            self.stdout.write(f'\n📈 Final Status: {final_approved}/{final_total} TeamMembers approved')
        
        self.stdout.write('\n💡 Usage Examples:')
        self.stdout.write('  # See what would happen')
        self.stdout.write('  python manage.py approve_users --dry-run')
        self.stdout.write('')
        self.stdout.write('  # Approve all existing users')
        self.stdout.write('  python manage.py approve_users --auto-approve')
        self.stdout.write('')
        self.stdout.write('  # Create profiles for users without them')
        self.stdout.write('  python manage.py approve_users --create-missing')
        self.stdout.write('')
        self.stdout.write('  # Do everything at once')
        self.stdout.write('  python manage.py approve_users --auto-approve --create-missing')
        
        if unapproved_team_members > 0 or users_without_team_member > 0:
            if not options['auto_approve'] and not options['create_missing']:
                self.stdout.write('\n⚠️  To resolve the approval issues, run:')
                self.stdout.write('  python manage.py approve_users --auto-approve --create-missing')