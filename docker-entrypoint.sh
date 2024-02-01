#!/bin/sh

# Wait for the database to be ready
echo "Waiting for the database..."
while ! python3 manage.py wait_for_db; do
  sleep 2
done
echo "Database is ready."

# Apply migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Start the Django application
python3 manage.py runserver 0.0.0.0:8000
