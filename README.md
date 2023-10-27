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

# Quickstart: cloud

```console
docker build --no-cache --network host -t ccsa_recommend .
docker run -d -p 8000:8000 ccsa_recommend
```

```console
az login
az acr login --name chancog
docker tag ccsa_recommend:latest chancog.azurecr.io/ccsa_recommend:v0.1.1
docker push chancog.azurecr.io/ccsa_recommend:v0.1.1
```

Modify deployment.yaml to have the same name and version, then deploy:

```console
kubectl apply -f deployment.yaml
```

Get info about the services:

```console
kubectl get svc
```

NAME                     TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
ccsa-generate-service    LoadBalancer   10.0.125.203   104.42.9.175     80:30375/TCP   40h
ccsa-recommend-service   LoadBalancer   10.0.92.32     20.253.217.145   80:30694/TCP   19s
kubernetes               ClusterIP      10.0.0.1       <none>           443/TCP        42h

In this example, 

Use when needed (kubernetes does nothing if deployment.yaml is unchanged, even if the image has been changed):

```console
kubectl delete deployment ccsa-recommend-deployment
kubectl delete svc ccsa-recommend-service
```