#!/bin/sh
set -e

echo "Waiting for database..."

until python -c "
import os
import psycopg2

url = os.environ['DATABASE_URL']
url = url.replace('postgresql+psycopg2', 'postgresql')

conn = psycopg2.connect(url)
conn.close()
"; do
    sleep 2
done

echo "Database connection ready."
echo "Running migrations..."
if ! alembic upgrade head; then
    echo "[CRITICAL ERROR] Alembic migration failed! Exiting backend startup."
    exit 1
fi

echo "Migrations executed successfully."
echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000