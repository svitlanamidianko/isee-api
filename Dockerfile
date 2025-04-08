# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.6

FROM python:${PYTHON_VERSION}-slim

LABEL fly_launch_runtime="flask"

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p "/app/assets/birthday_cards"

# Copy your data and assets
COPY data/ /app/data/
COPY assets/birthday_cards/* /app/assets/birthday_cards/

# Copy the rest of your application
COPY . .

# Make sure the app can access the directories
RUN chmod -R 755 /app/data
RUN chmod -R 755 /app/assets/birthday_cards

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

# List contents for debugging during build
RUN ls -la "/app/assets/birthday_cards"

# Use gunicorn for production with proper configuration
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
