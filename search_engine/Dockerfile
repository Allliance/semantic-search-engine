# backend/Dockerfile
FROM python:3.8-slim

WORKDIR /app/semantic_search_backend

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and collect static files
RUN python manage.py migrate && \
    python manage.py collectstatic --noinput

# Run the application
CMD ["gunicorn", "semantic_search_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
