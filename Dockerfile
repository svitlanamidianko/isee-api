# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.6

FROM python:${PYTHON_VERSION}-slim

LABEL fly_launch_runtime="flask"

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p "/app/assets/dixit cards"

# Copy your data and assets
COPY data/ /app/data/
COPY "assets/dixit cards"/* "/app/assets/dixit cards/"

# Copy the rest of your application
COPY . .

# Make sure the app can access the directories
RUN chmod -R 755 /app/data
RUN chmod -R 755 "/app/assets/dixit cards"

# List contents for debugging during build
RUN ls -la "/app/assets/dixit cards"

CMD ["python", "app.py"]
