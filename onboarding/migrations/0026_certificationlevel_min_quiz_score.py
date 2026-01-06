# Quick fix migration to add min_quiz_score field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0025_add_training_sections_with_videos'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificationlevel',
            name='min_quiz_score',
            field=models.PositiveIntegerField(default=70, help_text='Minimum passing score percentage for quizzes'),
        ),
    ]
