# core-recommender

# Overview
Core-Recommender is an API that enables users to receive movie recommendations. With this API, users can search for and discover films that align with their preferences. Core-Recommender provides film recommendations that facilitate users in finding movies that match their tastes.


# Requirements
    Python 3.9+

# Installation

Install using pip

pip install -r requirements.txt

Check if any changes schema of the database

python manage.py makemigrations

python manage.py migrate

# Runserver

python manage.py runserver

server running default on localhost:8000

# Quickstart: local

```console
docker build --no-cache --network host -t ccsa_recommend .
docker run -d -p 8000:8000 ccsa_recommend
```
