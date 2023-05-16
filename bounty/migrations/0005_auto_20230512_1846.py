# Generated by Django 3.2.18 on 2023-05-12 18:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bounty', '0004_auto_20230502_2253'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bountyhunter',
            name='bounty',
        ),
        migrations.RemoveField(
            model_name='bountyhunter',
            name='candidate_name',
        ),
        migrations.RemoveField(
            model_name='bountyhunter',
            name='candidate_profile',
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='address_line1',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='address_line2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='github_profile',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='state',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bountyhunter',
            name='zip_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='BountySubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_url', models.URLField()),
                ('notes', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('bounty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bounty.bounty')),
                ('bounty_hunter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BountySetter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('address_line1', models.CharField(blank=True, max_length=255, null=True)),
                ('address_line2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=20, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
