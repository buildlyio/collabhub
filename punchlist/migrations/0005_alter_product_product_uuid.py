# Generated by Django 3.2.25 on 2024-08-30 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('punchlist', '0004_auto_20240830_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_uuid',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
    ]