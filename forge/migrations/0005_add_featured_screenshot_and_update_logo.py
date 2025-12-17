# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forge', '0004_auto_20251204_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='forgeapp',
            name='featured_screenshot',
            field=models.URLField(blank=True, help_text='Featured screenshot displayed on marketplace listing', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='forgeapp',
            name='logo_url',
            field=models.URLField(blank=True, help_text='App logo (uses default TheForge logo if not provided)', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='forgeapp',
            name='screenshots',
            field=models.JSONField(blank=True, default=list, help_text='List of up to 2 additional screenshot URLs'),
        ),
    ]
