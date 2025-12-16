# Generated manually to handle M2M to through model conversion

from django.db import migrations, models
import django.db.models.deletion


def migrate_existing_assignments(apps, schema_editor):
    """Migrate existing M2M relationships to through model"""
    Customer = apps.get_model('onboarding', 'Customer')
    CustomerDeveloperAssignment = apps.get_model('onboarding', 'CustomerDeveloperAssignment')
    
    # Get the through table for the old M2M
    through_model = Customer.assigned_developers.through
    
    for customer in Customer.objects.all():
        for developer in customer.assigned_developers.all():
            CustomerDeveloperAssignment.objects.get_or_create(
                customer=customer,
                developer=developer,
                defaults={'status': 'pending'}
            )


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0012_contract_customer'),
    ]

    operations = [
        # Add share_token field
        migrations.AddField(
            model_name='customer',
            name='share_token',
            field=models.CharField(blank=True, help_text='Unique token for shareable URL', max_length=64, unique=True),
        ),
        
        # Create the through model
        migrations.CreateModel(
            name='CustomerDeveloperAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, help_text='Customer notes about this developer')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='onboarding.customer')),
                ('developer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='onboarding.teammember')),
            ],
            options={
                'ordering': ['-assigned_at'],
                'unique_together': {('customer', 'developer')},
            },
        ),
        
        # Migrate existing data
        migrations.RunPython(migrate_existing_assignments, migrations.RunPython.noop),
        
        # Remove old M2M field
        migrations.RemoveField(
            model_name='customer',
            name='assigned_developers',
        ),
        
        # Add new M2M field with through model
        migrations.AddField(
            model_name='customer',
            name='assigned_developers',
            field=models.ManyToManyField(related_name='assigned_to_customers', through='onboarding.CustomerDeveloperAssignment', to='onboarding.teammember'),
        ),
    ]
