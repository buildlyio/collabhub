# Generated by Django 3.2.25 on 2024-09-04 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('punchlist', '0007_auto_20240831_0013'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='completeness_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='feasibility_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='gemini_completeness_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='gemini_feasibility_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='gemini_marketability_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='gemini_originality_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='gemini_summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='marketability_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='originality_score',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]