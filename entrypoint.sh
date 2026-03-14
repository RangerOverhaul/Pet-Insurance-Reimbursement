#!/bin/sh
set -e

echo ">>> Applying migrations..."
python manage.py makemigrations users --no-input
python manage.py makemigrations pets --no-input
python manage.py makemigrations claims --no-input
python manage.py migrate --no-input

echo ">>> Starting server..."
exec python manage.py runserver 0.0.0.0:8000