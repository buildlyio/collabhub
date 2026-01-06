# Migration to add date fields to TeamTraining model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0026_certificationlevel_min_quiz_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamtraining',
            name='start_date',
            field=models.DateField(blank=True, help_text='When this training becomes available', null=True),
        ),
        migrations.AddField(
            model_name='teamtraining',
            name='end_date',
            field=models.DateField(blank=True, help_text='When this training closes/expires', null=True),
        ),
        migrations.AddField(
            model_name='teamtraining',
            name='due_date',
            field=models.DateField(blank=True, help_text='Complete by date for this training', null=True),
        ),
    ]
