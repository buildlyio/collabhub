# Generated by Django 3.2.24 on 2025-02-18 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0005_certificationexam_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='descr',
            field=models.TextField(blank=True),
        ),
    ]
