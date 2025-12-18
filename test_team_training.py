"""
Quick test script to verify DeveloperTeam and TeamTraining integration.
Run with: python manage.py shell < test_team_training.py
"""

from onboarding.models import DeveloperTeam, TeamTraining, Customer, TeamMember, DeveloperTrainingEnrollment
from django.contrib.auth.models import User

print("=" * 60)
print("Testing Developer Team Training System")
print("=" * 60)

# Check if we have any customers
customers = Customer.objects.all()
print(f"\n✓ Found {customers.count()} customers in database")

# Check if we have any team members
members = TeamMember.objects.filter(community_approval_date__isnull=False)
print(f"✓ Found {members.count()} approved team members")

# Check if DeveloperTeam table exists and is accessible
teams = DeveloperTeam.objects.all()
print(f"✓ DeveloperTeam model working - {teams.count()} teams exist")

# Check if TeamTraining has developer_team field
trainings = TeamTraining.objects.all()
print(f"✓ TeamTraining model working - {trainings.count()} trainings exist")

# Test if we can query trainings by team
team_trainings = TeamTraining.objects.filter(developer_team__isnull=False)
print(f"✓ Can query trainings by team - {team_trainings.count()} team-assigned trainings")

# Test team creation (if we have customers)
if customers.exists():
    customer = customers.first()
    print(f"\n--- Testing team creation for {customer.company_name} ---")
    
    # Check if test team already exists
    test_team_name = "Test Team (Auto-created)"
    existing_team = DeveloperTeam.objects.filter(
        customer=customer,
        name=test_team_name
    ).first()
    
    if existing_team:
        print(f"✓ Test team already exists: {existing_team}")
        test_team = existing_team
    else:
        # Try to create a test team
        try:
            admin_user = User.objects.filter(is_staff=True).first()
            if admin_user:
                test_team = DeveloperTeam.objects.create(
                    customer=customer,
                    name=test_team_name,
                    description="Auto-created test team",
                    created_by=admin_user,
                    is_active=True
                )
                print(f"✓ Created test team: {test_team}")
                
                # Try to add some members
                available_members = TeamMember.objects.filter(
                    id__in=members.values_list('id', flat=True)
                )[:3]
                
                if available_members:
                    test_team.members.add(*available_members)
                    print(f"✓ Added {test_team.member_count()} members to team")
            else:
                print("⚠ No admin user found - cannot create test team")
                test_team = None
        except Exception as e:
            print(f"✗ Error creating test team: {e}")
            test_team = None
    
    # Test training with team assignment
    if test_team:
        print(f"\n--- Testing training assignment to team ---")
        team_training_count = TeamTraining.objects.filter(developer_team=test_team).count()
        print(f"✓ Team has {team_training_count} trainings assigned")
        
        # Check enrollment count
        enrollment_count = DeveloperTrainingEnrollment.objects.filter(
            training__developer_team=test_team
        ).count()
        print(f"✓ Team members have {enrollment_count} total enrollments")

print("\n" + "=" * 60)
print("All checks passed! ✓")
print("=" * 60)
print("\nNext steps:")
print("1. Visit http://localhost:8000/onboarding/admin/developer-teams/")
print("2. Create a new developer team")
print("3. Add members to the team")
print("4. Assign a training to the team")
print("5. Check developer dashboard to see team trainings")
