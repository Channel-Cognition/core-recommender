Make sure you create recommender/.env and fill in the following variables:

DEBUG= # boolean value (true/false)

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=

GPT_35_DEPLOY_NAME=
SECRET_KEY=

DB_IGNORE_SSL= # boolean value (true/false)

COSMOS_URL=
COSMOS_KEY=
COSMOS_DB_NAME=


AZURE_OPENAI_KEY=
AZURE_OPENAI_ENDPOINT=
TVDB_KEY=

PINECONE_API_KEY=
PINECONE_API_ENV=
IS_FAST_DEV=

ENV_CORS_ALLOWED_ORIGINS=http://localhost:3000 https://purple-forest-02cc0fc0f.4.azurestaticapps.net
ENV_CORS_ALLOW_CREDENTIALS=true
ENV_CORS_ALLOW_HEADERS=Authorization Content-Type
ENV_CORS_ALLOW_METHODS=GET POST PUT DELETE

OPEN_AI_API_KEY=

PINECONE_API_KEY=
PINECONE_API_ENV=
PINECONE_ITEMS_INDEX_NAME=

    If you change POSTGRES_PORT or REDIS_PORT be sure to update those values in docker-compose.yaml

Once you have the above .env file, navigate to your project root (right where docker-compose.yaml is) and run:

docker compose up -d
docker compose up --build

This will create a postgresql database, redis, celery and django project that runs in the background for you. To bring down these just run:

docker compose down

The data in the database will be persistent so you can run docker compose up -d again with confidence.

Django project is ready to be used locally.

To fully delete the running images:

```console
docker-compose down --rmi all --volumes --remove-orphans
```

When you modfiy the database schema, you need to reapply migrations. First, identify the ID for the API container (recommender-web-1):


```console
docker ps
```

This will yield something like this:

CONTAINER ID   IMAGE                        COMMAND                  CREATED         STATUS          PORTS                              NAMES
1b5c0162c4ae   recommender-celery           "celery --app=recomm…"   5 minutes ago   Up 18 seconds                                      celery1
2a0205c64873   django-core-recommender:v1   "gunicorn recommende…"   5 minutes ago   Up 18 seconds   0.0.0.0:8000->8000/tcp             recommender-web-1
12ec22796e54   redis                        "redis-server --appe…"   2 hours ago     Up 19 seconds   6379/tcp, 0.0.0.0:6388->6388/tcp   recommender-redis_db-1
0d5dba8491a1   postgres:13-alpine           "docker-entrypoint.s…"   2 hours ago     Up 19 seconds   0.0.0.0:5432->5432/tcp             recommender-postgres_db-1

Next enter the container and do the migrations:

```console
docker exec -it 2a0205c64873 sh
python manage.py migrate
```