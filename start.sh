#!/bin/bash
set -e

echo "--> Running migrations..."
python manage.py migrate --run-syncdb

echo "--> Running initial setup..."
python manage.py init_setup

echo "--> Collecting static files..."
python manage.py collectstatic --noinput

echo "--> Starting Gunicorn..."
exec gunicorn navratri_project.wsgi --log-file -
