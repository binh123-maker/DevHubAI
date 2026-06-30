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

echo "Running migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000