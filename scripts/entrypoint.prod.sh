#!/bin/sh

set -e # Exit immediately if a command exits with a non-zero status.

python manage.py collectstatic --noinput
python manage.py migrate

# Wait for the database to be ready
echo "Waiting for the database..."
while ! python3 manage.py wait_for_db; do
  sleep 2
done
echo "Database is ready."

gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers 3