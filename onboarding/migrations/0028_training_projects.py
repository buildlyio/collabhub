# Migration to add TrainingProject and ProjectSubmission models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('onboarding', '0027_teamtraining_dates'),
    ]

    operations = [
        # Create TrainingProject model
        migrations.CreateModel(
            name='TrainingProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(help_text='Detailed description of the project requirements')),
                ('order', models.PositiveIntegerField(default=0, help_text='Order of this project within the training')),
                ('requirements', models.TextField(blank=True, help_text='Specific requirements or acceptance criteria')),
                ('resources_hint', models.TextField(blank=True, help_text='Helpful resources or hints for completing the project')),
                ('max_score', models.PositiveIntegerField(default=10, help_text='Maximum score (default 1-10)')),
                ('passing_score', models.PositiveIntegerField(default=7, help_text='Minimum score to pass')),
                ('due_date', models.DateField(blank=True, help_text='Due date for this project', null=True)),
                ('is_required', models.BooleanField(default=True, help_text='Is this project required to complete the training?')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('training', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='onboarding.teamtraining')),
            ],
            options={
                'ordering': ['training', 'order'],
                'unique_together': {('training', 'order')},
            },
        ),
        # Create ProjectSubmission model
        migrations.CreateModel(
            name='ProjectSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_url', models.URLField(help_text='GitHub repository URL for the project')),
                ('student_description', models.TextField(blank=True, help_text="Student's description of their submission")),
                ('student_notes', models.TextField(blank=True, help_text='Additional notes from the student')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('in_review', 'In Review'), ('revision_requested', 'Revision Requested'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='draft', max_length=20)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('score', models.PositiveIntegerField(blank=True, help_text='Score from 1-10 (or up to max_score)', null=True)),
                ('teacher_notes', models.TextField(blank=True, help_text='Feedback and notes from the reviewer')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('developer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_submissions', to='onboarding.teammember')),
                ('enrollment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_submissions', to='onboarding.developertrainingenrollment')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='onboarding.trainingproject')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at', '-created_at'],
                'unique_together': {('project', 'developer')},
            },
        ),
    ]
