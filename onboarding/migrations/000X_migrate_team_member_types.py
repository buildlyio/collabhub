from django.db import migrations

def migrate_team_member_types(apps, schema_editor):
    TeamMemberType = apps.get_model('onboarding', 'TeamMemberType')
    TeamMember = apps.get_model('onboarding', 'TeamMember')

    TEAM_MEMBER_TYPES = [
        ('all', 'Everyone'),
        ('buildly-hire-frontend', 'Buildly Hire Frontend'),
        ('buildly-hire-backend', 'Buildly Hire Backend'),
        ('buildly-hire-ai', 'Buildly Hire AI'),
        ('buildly-hire-marketing', 'Buildly Hire Marketing'),
        ('buildly-hire-product', 'Buildly Hire Product'),
        ('buildly-hire-marketing-intern', 'Buildly Hire Marketing Intern'),
        ('community-member-generic', 'Generic Community Member'),
        ('community-frontend', 'Community Member Frontend'),
        ('community-backend', 'Community Member Backend'),
        ('community-product', 'Community Member Product'),
        ('community-ai', 'Community Member AI'),
        ('community-ui-designer', 'Community Member UI Designer'),
        ('community-ux', 'Community Member UX'),
        ('community-advisor', 'Community Member Advisor'),
        ('community-software-agency', 'Community Member Software Agency'),
        ('community-marketing-agency', 'Community Member Marketing Agency'),
        ('community-design-agency', 'Community Member Design Agency'),
    ]

    # 1. Create TeamMemberType objects for each type in TEAM_MEMBER_TYPES
    key_to_obj = {}
    for key, label in TEAM_MEMBER_TYPES:
        obj, created = TeamMemberType.objects.get_or_create(key=key, defaults={'label': label})
        if not created and obj.label != label:
            obj.label = label
            obj.save()
        key_to_obj[key] = obj

    # 2. For each TeamMember, set profile_types based on team_member_type
    for member in TeamMember.objects.all():
        if member.team_member_type:
            tmt_obj = key_to_obj.get(member.team_member_type)
            if tmt_obj:
                member.profile_types.add(tmt_obj)

class Migration(migrations.Migration):
    dependencies = [
        ('onboarding', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_team_member_types),
    ]
