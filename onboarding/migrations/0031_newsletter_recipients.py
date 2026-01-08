# Migration for NewsletterRecipient model and newsletter status tracking

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0030_communitynewsletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitynewsletter',
            name='failed_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of failed email sends'),
        ),
        migrations.AddField(
            model_name='communitynewsletter',
            name='pending_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of pending email sends'),
        ),
        migrations.AddField(
            model_name='communitynewsletter',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('sending', 'Sending'), ('completed', 'Completed'), ('paused', 'Paused')], default='completed', max_length=20),
        ),
        migrations.CreateModel(
            name='NewsletterRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to='onboarding.communitynewsletter')),
                ('developer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='onboarding.teammember')),
            ],
            options={
                'ordering': ['status', 'email'],
                'unique_together': {('newsletter', 'email')},
            },
        ),
    ]
