#!/usr/bin/env bash

set -e

echo $(date -u) "- Migrating"
python manage.py makemigrations
python manage.py migrate

echo $(date -u) "- Creating admin user"
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(email='radhika@buildly.io').delete(); User.objects.create_superuser('radhikapatel', 'radhika@buildly.io', 'Maddy@1102')"

echo $(date -u) "- Running the server"
gunicorn mysite.wsgi --config mysite/gunicorn_conf.py --workers 2 --timeout 1200 --reload
