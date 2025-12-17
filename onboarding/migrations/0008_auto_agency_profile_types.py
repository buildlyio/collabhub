# Generated migration for agency and profile types

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0007_auto_20250310_2257'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMemberType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, unique=True)),
                ('label', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['label'],
            },
        ),
        migrations.AddField(
            model_name='teammember',
            name='is_independent',
            field=models.BooleanField(default=True, help_text='Is this an independent developer?'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='agency',
            field=models.ForeignKey(blank=True, help_text='Associated agency if not independent', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_members', to='onboarding.DevelopmentAgency'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='agency_name_text',
            field=models.CharField(blank=True, help_text='Agency name if not registered on platform', max_length=255),
        ),
        migrations.AddField(
            model_name='teammember',
            name='profile_types',
            field=models.ManyToManyField(blank=True, help_text='Multiple profile types', related_name='team_members', to='onboarding.TeamMemberType'),
        ),
    ]
