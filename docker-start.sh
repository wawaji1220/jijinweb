#!/bin/bash

set -e

echo "=== Django Fund Management System - Docker Start ==="

# Wait for database initialization
if [ ! -f "db/db.sqlite3" ]; then
    echo "Database not found, initializing..."
    mkdir -p db
fi

# Database migration
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if not exists
echo "Checking superuser..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jijinweb.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating default superuser...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Default admin account: admin / admin123')
else:
    print('Superuser already exists')
"

echo "=== Starting Django Server and Scheduler ==="

# Start scheduler in background
python manage.py start_scheduler &
PID_SCHEDULER=$!

# Start Django development server
python manage.py runserver 0.0.0.0:8000

# Wait for scheduler process
wait $PID_SCHEDULER
