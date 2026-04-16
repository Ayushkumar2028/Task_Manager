#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Creating initial data..."
python manage.py create_initial_data || true
