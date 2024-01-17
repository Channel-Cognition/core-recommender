#!/bin/bash
python manage.py migrate --noinput
gunicorn --reload -b 0.0.0.0:8000 --timeout 120 recommender.wsgi:application