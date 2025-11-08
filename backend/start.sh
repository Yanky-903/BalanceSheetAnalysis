#!/usr/bin/env bash
set -e

# Wait for DB to be available (if using Postgres managed by Render)
if [ -n "$DATABASE_URL" ]; then
  # simple wait loop: try to connect using psql if present, else sleep fixed
  # You can add more robust wait-for logic if desired.
  echo "DATABASE_URL present, waiting a few seconds for DB..."
  sleep 3
fi

# run database create (SQLAlchemy create_all is in main.py) and seed
python -c "from app import seed_data; seed_data.seed()"

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
