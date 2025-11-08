# Dockerfile (place this in the repo root)
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install minimal system deps required for psycopg2 and building wheels
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copy backend source
COPY backend /app

# Ensure start script is executable
RUN chmod +x /app/start.sh

# Use port env variable from Render (defaults to 8000 if not set)
ENV PORT=8000

# Run the start script (which seeds DB and starts uvicorn)
CMD [ "/app/start.sh" ]
