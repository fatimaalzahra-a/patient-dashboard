#!/bin/bash

echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Makemigrations..."
python manage.py makemigrations 
echo "Applying migrations..."
python manage.py migrate

echo "Starting server..."
exec gunicorn PatientDashboard.wsgi:application --bind 0.0.0.0:8000 --reload
