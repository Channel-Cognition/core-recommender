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
```

```console
az login
az acr login --name chancog
docker build --no-cache --network host -t ccsa_recommend .
docker tag ccsa_recommend:latest chancog.azurecr.io/ccsa_recommend:v0.1.3
docker push chancog.azurecr.io/ccsa_recommend:v0.1.3
```

Create a configuration map for the staging environmental variables:

```console
kubectl create configmap ccsa-recommend-env --from-env-file=.env.stage
```

Optionally, look at what this did behind the scenes:

```console
kubectl get configmap ccsa-recommend-env -o yaml
```

Deploy, see what pods we have, and look at the logs for any errors:

```console
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs <pod-name>
```

Optionally, look at our deployments:

```console
kubectl get deployments
```

If necessary, you can force a deployment restart this way:

```console
kubectl rollout restart deployment/ccsa-recommend-deployment
```

To expose the IP we need to start a service. Start one, and see what services we have.


```console
kubectl apply -f ccsa-recommend-service.yaml
kubectl get services
```

This yields something like this:

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

# Setup (IGNORE FOR NOW)
IGNORE FOR NOW
These are some of the steps we need for using Azure key vault to set ENV variables in production. Presently, we are using .env locally and .env.stage for immge building, which is not wise long term since this places the ENV variables in our Docker image that is pushed to our repository.

If need be, install helm (this may require elevated privileges, and there are alternatives to choco):

```console
choco install kubernetes-helm
```

Update the Helm configuration so we can use/install akv2k8s and then install it:

```console
helm repo add spv-charts http://charts.spvapi.no
helm repo update
helm install akv2k8s spv-charts/akv2k8s --namespace akv2k8s --create-namespace
```

We need to give akv2k8s access to our key vault. To do so, we first must create a service principle, which is an Azure resource:

```console
az ad sp create-for-rbac --name akv2k8s-access-sp --skip-assignment
```

This will print out info like this if it's successful (the actual values are redacted, but can be obtained through the Azure portal, too):

{
  "appId": "",
  "displayName": "",
  "password": "",
  "tenant": ""
}

```console
kubectl create secret generic akv2k8s-secret --from-literal=clientid=<appId> --from-literal=clientsecret=<password> --namespace akv2k8s
```

az keyvault set-policy --name sa-env-dev-useast --spn <AppId> --secret-permissions get list


If necessary, list the appId again:

```console
az ad sp list --filter "displayName eq 'akv2k8s-access-sp'" --query "[].appId" -o tsv
```

```console
az keyvault set-policy --name sa-env-dev-useast --spn <appId> --secret-permissions get list
```

set up akv2k8s to use the secrets. If my understanding is correct, the following command only needs to be run once (akv2k8s will now continually sync with the values in the Azure key vault, including if you change them through the web portal):

```console
kubectl apply -f azurekeyvaultsecrets.yaml
```

