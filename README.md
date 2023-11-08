# core-recommender

# Overview
Core-Recommender is an API that enables users to receive movie recommendations. With this API, users can search for and discover films that align with their preferences. Core-Recommender provides film recommendations that facilitate users in finding movies that match their tastes.

# Local dev
## Local dev setup
TODO: We may need exactly Python 3.10
Install postgres, then make the database:

```console
createdb -U postgres sadev
```


Make a new user:

```console
psql -U postgres
CREATE USER <db_user> WITH PASSWORD '<password>';
GRANT ALL PRIVILEGES ON DATABASE sadev TO <db_user>;
GRANT USAGE ON SCHEMA public TO <db_user>;
ALTER DATABASE sadev OWNER TO <db_user>;
```

Check that postgres is ready:

```console
pg_isready
```

Place these in the local .env file:

POSTGRES_DB=sadev
POSTGRES_USER=<db_user>
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

Make a virtual environment:

```console
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Add following to .env:

ENV_CORS_ALLOWED_ORIGINS=http://localhost:3000
ENV_CORS_ALLOW_HEADERS=Origin X-Requested-With Content-Type Accept Authorization
ENV_CORS_ALLOW_METHODS=DELETE GET OPTIONS PATCH POST PUT
DEBUG=true
SECRET_KEY=Dummy
DB_IGNORE_SSL=true

Add the following to .env (values must be obtained):

COSMOS_URL
COSMOS_KEY
COSMOS_DB_NAME
TVDB_KEY
AZURE_OPENAI_KEY
AZURE_OPENAI_ENDPOINT
PINECONE_API_KEY
PINECONE_API_ENV

Optionally, set IS_FAST_DEV (it will be True if the value is exactly true, and False otherwise).

## Local dev cycle
If necessary, activate the virtual environment:

```console
python -m venv venv
```

If necessary, make migrations:

```console
python manage.py makemigrations
```

If necessary, make migrate:

```console
python manage.py migrate
```
Run the local server:


```console
python manage.py runserver
```


Check the local deployment (WARNING: the final / is not optional):

http://localhost:8000/api/docs/