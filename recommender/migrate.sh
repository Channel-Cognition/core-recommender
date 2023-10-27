#!/bin/bash

cd /app/
/opt/venv/bin/python manage.py wait_for_db
/opt/venv/bin/python manage.py migrate --noinput