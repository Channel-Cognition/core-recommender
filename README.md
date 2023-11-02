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

If necessary, build the wheel file in the chancog directory

```console
set BUILD_SOURCEBRANCHNAME=dev
```
Windows Powershell:

```console
$env:BUILD_SOURCEBRANCHNAME = "dev"
```

In the chancog repo, run
```console
python setup.py clean --all
python setup.py bdist_wheel
```

Copy the wheel file from/chancog/dist into /ccgenerate/wheels
Check that the name of the wheel file in Dockers is the same as in /wheels

Switch back to the core-recommender/recommnder directory. Make sure you have a complete .env file at that location. Then, build and run the Dockerfile:

```console
docker build --no-cache --network host -t ccsa_recommend .
docker compose up
```

Navigate to: http://localhost:8000/api/docs/

WARNING: The .env file should only be used for local dev. It is present in both .gitignore and .dockerignore.

# Quickstart: cloud (once only)
TBD

```console
az login
az aks create --resource-group sa-dev-useast --name sa-dev-useast --node-count 1 --enable-addons monitoring --generate-ssh-keys
az aks get-credentials --resource-group sa-dev-useast --name sa-dev-useast
```

Check the AKS cluster deployment by looking at our nodes:

```console
kubectl get nodes
```

You should see something like this:

NAME                                STATUS   ROLES   AGE     VERSION
aks-nodepool1-28562811-vmss000000   Ready    agent   2m56s   v1.26.6

Safely create a secret you can link to using PowerShell. ACR_REGISTRY
ACR_USERNAME, and ACR_PASSWORD must be defined in your .env file.

```console
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\create_secret.ps1
```

# Quickstart: cloud

```console
docker build --no-cache --network host -t ccsa_recommend .
docker run -d -p 8000:8000 ccsa_recommend
```

```console
az login
az acr login --name chancog
docker tag ccsa_recommend:latest chancog.azurecr.io/ccsa_recommend:v0.1.2
docker push chancog.azurecr.io/ccsa_recommend:v0.1.2
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

In this example, the swagger documentation should be viewable here:

http://20.253.217.145/api/docs/

Use the following commands when needed (kubernetes does nothing if deployment.yaml is unchanged, even if the image has been changed):

```console
kubectl delete deployment ccsa-recommend-deployment
kubectl delete svc ccsa-recommend-service
```