FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    g++ \
    gcc \
    libffi-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p static staticfiles media

# Collect static files (build-time env only)
RUN DEBUG=True SECRET_KEY=build-temp-key DATABASE_URL=postgresql://placeholder:placeholder@localhost:5432/placeholder python manage.py collectstatic --noinput

# Run migrations and start the application
CMD ["sh", "-c", "python manage.py migrate && python manage.py setup_oauth && gunicorn main.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]