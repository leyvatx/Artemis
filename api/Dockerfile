FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY base.txt .
RUN pip install --no-cache-dir -r base.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p logs staticfiles media

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8002

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
