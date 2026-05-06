#!/bin/sh

set -e

# Wait for the database to be ready

while ! python3 manage.py wait_for_db; do
  sleep 2
done


# Apply migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Start the Django application
python3 manage.py runserver 0.0.0.0:8000
