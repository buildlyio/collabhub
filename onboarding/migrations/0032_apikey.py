from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('onboarding', '0031_newsletter_recipients'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('partner', models.CharField(choices=[('labs', 'Buildly Labs'), ('other', 'Other')], default='labs', max_length=50)),
                ('key_type', models.CharField(choices=[('inbound', 'Inbound (Partner → CollabHub)'), ('outbound', 'Outbound (CollabHub → Partner)')], max_length=20)),
                ('key_prefix', models.CharField(help_text='First 8 chars of key for identification', max_length=20)),
                ('key_hash', models.CharField(help_text='SHA-256 hash of the full key', max_length=64)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'verbose_name': 'API Key',
                'verbose_name_plural': 'API Keys',
                'ordering': ['-created_at'],
            },
        ),
    ]
