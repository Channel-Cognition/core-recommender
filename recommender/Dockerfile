FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy local directory contents to /app directory in the container
COPY . /app
WORKDIR /app

# Upgrade pip and install required python packages
RUN python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy wheel files over [this may be superfluous]
COPY wheels /wheels 

# Install all wheel files from the /wheels directory
RUN pip install /wheels/*.whl

# Command to run Django's runserver
CMD ["gunicorn", "recommender.wsgi:application", "--bind", "0.0.0.0:8000"]