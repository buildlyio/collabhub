#!/bin/bash
set -e

# Run Django makemigrations, migrate, and collectstatic
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
