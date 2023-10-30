# Use the slim-buster version of Python 3.10
FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY ./recommender/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install custom wheel files
COPY wheels /wheels
RUN pip install /wheels/chancog-0.3.dev125-py3-none-any.whl

# Copy the entire project inside the container
COPY ./recommender /app

# Setting environment variable for Django settings module
ENV DJANGO_SETTINGS_MODULE=recommender.settings

# Expose the port the app runs on
EXPOSE 8000

# Command to run Django's runserver
CMD ["gunicorn", "recommender.wsgi:application", "--bind", "0.0.0.0:8000"]