# Load environment variables from .env file
$env:ACR_REGISTRY = (Get-Content .env | Where-Object { $_ -match 'ACR_REGISTRY' }).Split('=')[1]
$env:ACR_USERNAME = (Get-Content .env | Where-Object { $_ -match 'ACR_USERNAME' }).Split('=')[1]
$env:ACR_PASSWORD = (Get-Content .env | Where-Object { $_ -match 'ACR_PASSWORD' }).Split('=')[1]

# Create Kubernetes secret
kubectl create secret docker-registry acr-credentials `
    --docker-server=$env:ACR_REGISTRY `
    --docker-username=$env:ACR_USERNAME `
    --docker-password=$env:ACR_PASSWORD