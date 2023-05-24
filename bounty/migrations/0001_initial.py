# Generated by Django 3.2.18 on 2023-04-28 18:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bounty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Name your bounty, i.e. Fix Registration Error', max_length=255)),
                ('skills', models.CharField(blank=True, help_text='Skills Required to Fix your Issue', max_length=255)),
                ('level', models.CharField(blank=True, choices=[('Intern', 'Intern'), ('Junior', 'Junior'), ('Midlevel', 'Mid-Level'), ('Senior', 'Senior'), ('CTO', 'CTO')], help_text='Skill level - Select One', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Describe in detail the issue of person you are looking for')),
                ('certification', models.TextField(blank=True, help_text='Certifications required if any')),
                ('brief', models.FileField(blank=True, help_text='Document Upload', null=True, upload_to='')),
                ('amount', models.CharField(blank=True, choices=[('Small', '$25'), ('Medium', '$40'), ('Large', '$75'), ('XL', '$100'), ('XXL', '$200')], help_text='How Much in USD to get the work done.', max_length=255)),
                ('url', models.CharField(blank=True, help_text='Your GitHub Repository URL', max_length=255, null=True)),
                ('status', models.CharField(blank=True, choices=[('Draft', 'Draft'), ('Planned', 'Planned'), ('Started', 'Started'), ('Found', 'Found'), ('CANCELED', 'CANCELED')], default='DRAFT', help_text='Acitivate the Hunt', max_length=255)),
                ('repo_owner', models.CharField(max_length=100)),
                ('repo', models.CharField(max_length=100)),
                ('repo_access_token', models.CharField(max_length=100)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('edit_date', models.DateTimeField(blank=True, null=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('edit_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_paid', models.BooleanField(default=False)),
                ('plan', models.CharField(blank=True, max_length=255)),
                ('expriation_date', models.DateTimeField(blank=True, null=True)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('edit_date', models.DateTimeField(blank=True, null=True)),
                ('bounty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bounty.bounty')),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('priority', models.IntegerField()),
                ('complexity_estimate', models.IntegerField()),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('edit_date', models.DateTimeField(blank=True, null=True)),
                ('bounty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bounty.bounty')),
            ],
        ),
        migrations.CreateModel(
            name='BountyHunter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('candidate_name', models.CharField(blank=True, max_length=255)),
                ('candidate_profile', models.CharField(blank=True, max_length=255)),
                ('candidate_certification', models.CharField(blank=True, max_length=255)),
                ('candidate_resume', models.CharField(blank=True, max_length=255)),
                ('candidate_skills', models.CharField(blank=True, max_length=255)),
                ('candidate_level', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(blank=True, max_length=255)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('edit_date', models.DateTimeField(blank=True, null=True)),
                ('bounty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bounty.bounty')),
            ],
        ),
    ]