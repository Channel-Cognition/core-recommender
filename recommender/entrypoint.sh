#!/bin/bash
celery -A recommender worker -l info --detach
gunicorn --reload -b 0.0.0.0:8000 --timeout 120 recommender.wsgi:application
