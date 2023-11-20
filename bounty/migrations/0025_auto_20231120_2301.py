# Generated by Django 3.2.18 on 2023-11-20 23:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bounty', '0024_alter_bug_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='bug',
            name='issue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bug_issue', to='bounty.issue'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='bug',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issue_bug', to='bounty.bug'),
        ),
    ]
