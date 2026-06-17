#!/bin/bash
echo "===================================="
echo "  Fund NAV Real-time Estimation System"
echo "===================================="
echo

echo "[1/5] Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Virtual environment not found, creating..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
echo "Virtual environment activated"
echo

echo "[2/5] Checking database..."
if [ ! -f "db.sqlite3" ]; then
    echo "Initializing database..."
    python manage.py makemigrations
    python manage.py migrate
    echo "Superuser: admin (set password manually)"
else
    echo "Database already exists"
fi
echo

echo "[3/5] Collecting static files..."
python manage.py collectstatic --noinput
echo

echo "[4/5] Starting scheduler..."
python scheduler.py &
SCHEDULER_PID=$!
echo "Scheduler started (PID: $SCHEDULER_PID)"
echo

echo "[5/5] Starting Django dev server..."
echo
echo "===================================="
echo " URL: http://127.0.0.1:8000"
echo " Admin: http://127.0.0.1:8000/admin"
echo "===================================="
echo

python manage.py runserver

# Cleanup
kill $SCHEDULER_PID 2>/dev/null
