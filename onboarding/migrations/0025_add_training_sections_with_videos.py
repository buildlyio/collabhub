# Generated migration for training sections with videos

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0024_merge_20251229_1817'),
    ]

    operations = [
        # Create TrainingSection model
        migrations.CreateModel(
            name='TrainingSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Order of this section within the training')),
                ('start_date', models.DateField(blank=True, help_text='When this section becomes available', null=True)),
                ('end_date', models.DateField(blank=True, help_text='Complete by date for this section', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('training', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='onboarding.teamtraining')),
                ('quizzes', models.ManyToManyField(blank=True, help_text='Quizzes to complete at the end of this section', related_name='training_sections', to='onboarding.Quiz')),
            ],
            options={
                'ordering': ['training', 'order', 'start_date'],
                'unique_together': {('training', 'order')},
            },
        ),
        # Create SectionResource model
        migrations.CreateModel(
            name='SectionResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Order of this resource within the section')),
                ('link', models.URLField(blank=True, help_text='URL to external resource')),
                ('document', models.FileField(blank=True, help_text='Upload a document or file', upload_to='section_resources/')),
                ('video_source', models.CharField(choices=[('none', 'No Video'), ('youtube', 'YouTube'), ('cloudflare', 'CloudFlare Stream'), ('mp4', 'Direct MP4 URL'), ('vimeo', 'Vimeo')], default='none', max_length=20)),
                ('video_url', models.URLField(blank=True, help_text='Video URL (YouTube, CloudFlare, Vimeo link, or direct MP4 URL)')),
                ('video_embed_code', models.TextField(blank=True, help_text='Custom embed code if needed (optional - auto-generated for YouTube/CloudFlare/Vimeo)')),
                ('video_duration_minutes', models.PositiveIntegerField(blank=True, help_text='Estimated video duration in minutes', null=True)),
                ('estimated_time_minutes', models.PositiveIntegerField(blank=True, help_text='Estimated time to complete this resource in minutes', null=True)),
                ('is_required', models.BooleanField(default=True, help_text='Is this resource required to complete the section?')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='section_resources', to='onboarding.trainingsection')),
            ],
            options={
                'ordering': ['section', 'order'],
                'unique_together': {('section', 'order')},
            },
        ),
        # Create SectionProgress model
        migrations.CreateModel(
            name='SectionProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='section_progress', to='onboarding.developertrainingenrollment')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='onboarding.trainingsection')),
            ],
            options={
                'ordering': ['section__order'],
                'unique_together': {('enrollment', 'section')},
            },
        ),
        # Create ResourceProgress model
        migrations.CreateModel(
            name='ResourceProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('time_spent_minutes', models.PositiveIntegerField(default=0, help_text='Time spent on this resource in minutes')),
                ('notes', models.TextField(blank=True, help_text='Developer notes on this resource')),
                ('section_progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_progress', to='onboarding.sectionprogress')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='onboarding.sectionresource')),
            ],
            options={
                'unique_together': {('section_progress', 'resource')},
            },
        ),
        # Add new fields to CertificationLevel model
        migrations.AddField(
            model_name='certificationlevel',
            name='required_trainings',
            field=models.ManyToManyField(blank=True, help_text='Trainings that must be completed for this certification', related_name='certifications', to='onboarding.TeamTraining'),
        ),
        migrations.AddField(
            model_name='certificationlevel',
            name='required_sections',
            field=models.ManyToManyField(blank=True, help_text='Specific training sections required for this certification', related_name='certifications', to='onboarding.TrainingSection'),
        ),
        migrations.AddField(
            model_name='certificationlevel',
            name='required_quizzes',
            field=models.ManyToManyField(blank=True, help_text='Quizzes that must be passed for this certification', related_name='certifications', to='onboarding.Quiz'),
        ),
        # min_quiz_score moved to migration 0026
    ]
