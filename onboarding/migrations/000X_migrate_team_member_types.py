from django.db import migrations
from onboarding.models import TEAM_MEMBER_TYPES

def migrate_team_member_types(apps, schema_editor):
    TeamMemberType = apps.get_model('onboarding', 'TeamMemberType')
    TeamMember = apps.get_model('onboarding', 'TeamMember')

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
