Build container

docker login

docker build -f Dockerfile -t registry.digitalocean.com/django-recommender/django-core-recommender:latest . 

    Push Container with 2 tags: latest and random
docker push registry.digitalocean.com/django-recommender/django-core-recommender --all-tags

    Update secrets (if needed)
kubectl delete secret k8s-core-recommender-env
kubectl create secret generic k8s-core-recommender-env --from-env-file=.kube/.env.prod

    apply core recommender service
kubectl apply -f k8s/k8s-core-recommender.yaml
    
    apply redis service
kubectl apply -f k8s/k8s-redis.yaml

    Roll Update(if needed):
kubectl rollout restart deployment/django-k8s-core-recommender
