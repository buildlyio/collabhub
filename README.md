# devhunter_app
Beta version of the DevHunter app

## Getting Started

First create a virtualenv
``virtualenv venv``
``source venv/bin/activate``

Then install requirements
``pip3 install -r requirements.txt``

Then Run Migrations
``python manage.py migrate``

Then Run the Test server
``python manage.py runserver``

Create a SuperUser
``python manage.py createsuperuser``
