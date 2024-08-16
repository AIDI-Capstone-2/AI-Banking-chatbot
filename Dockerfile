# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install any system dependencies required by your application
RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    gcc \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the static directory exists if needed
RUN mkdir -p /app/static

# Expose the port on which the app will run
EXPOSE 8080

# Run the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
