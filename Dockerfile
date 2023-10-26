# Use the slim-buster version of Python 3.10
FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project inside the container
COPY ./recommender /app/recommender

# Setting environment variable for Django settings module
ENV DJANGO_SETTINGS_MODULE=recommender.settings

# Expose the port the app runs on
EXPOSE 8000

# Command to run Django's runserver
CMD ["python", "recommender/manage.py", "runserver", "0.0.0.0:8000"]