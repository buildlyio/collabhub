from django.core.management.base import BaseCommand, CommandError
from monitorsites.health_check import check_all_sites

"""
Custom Manage.py command to be executed by cron
https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/

To Execute:
python manage.py check
"""

class Command(BaseCommand):
    help = 'Execute cron to check health of app'

    def handle(self, *args, **options):
        try:
            check_all_sites()
        except Exception as e:
            print(e)
            print('%s' % type(e))

        self.stdout.write(self.style.SUCCESS("Successfully ran Cron"))