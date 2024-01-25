"""
Django settings for recommender project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
from chancog.cosmos import CosmosHandler
from chancog.llm import OpenAIHandler, CorrectingOpenAIHandler
from chancog.sagenerate.tvdb import TVDBHandler
from chancog.sagenerate.openlibrary import OpenLibraryHandler
from chancog.llm import PineconeManager
from openai import AzureOpenAI

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

ENV_ALLOWED_HOST = os.environ.get("ENV_ALLOWED_HOST")
ALLOWED_HOSTS = []
if ENV_ALLOWED_HOST:
    ALLOWED_HOSTS = ENV_ALLOWED_HOST.split(' ')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

DEBUG = str(os.getenv('DEBUG')) == "true"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",

    "corsheaders",
    "drf_spectacular",
    "rest_framework",
    "rest_framework.authtoken",
    'channels',
    'django_celery_results',

    "convos",
    "movies",
    "suggestions",
    "user",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware"]

ROOT_URLCONF = "recommender.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "recommender.wsgi.application"
ASGI_APPLICATION = "recommender.asgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DB_USERNAME = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_DATABASE = os.environ.get("POSTGRES_DB")
DB_HOST = os.environ.get("POSTGRES_HOST")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_IS_AVAIL = all([
    DB_USERNAME,
    DB_PASSWORD,
    DB_DATABASE,
    DB_HOST,
    DB_PORT
])
DB_IGNORE_SSL =os.environ.get("DB_IGNORE_SSL") == "true"

if DB_IS_AVAIL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_DATABASE,
            'USER': DB_USERNAME,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }
    if not DB_IGNORE_SSL:
         DATABASES["default"]["OPTIONS"] = {
            "sslmode": "require"
         }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
AUTH_USER_MODEL = 'user.User'


# DEFAULT SNIPPET ONBOARDING
framing = "You are an assistant helping the user find new movies or TV show to watch. "
framing += "Be as succinct as is reasonable while still uniquely identifying items. "
framing += "Do not include items the user is no longer interested in."
framing += "Return a JSON with two base fields: text, which will be shown to the user, and new_items, "
framing += "which is a list of newly suggested items. Each item in new_items must contain an item_type field "
framing += "(e.g., movie) and should contain additional fields to uniquely specify the item "
framing += "(e.g., title and director for a movie)."

GREETING = "Hello, what are you looking for today?"

TRUNCATED_FRAMING = framing

AZURE_OPENAI_KEY=os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT=os.environ.get("AZURE_OPENAI_ENDPOINT")

COSMOS_URL = os.environ.get("COSMOS_URL")
COSMOS_KEY = os.environ.get("COSMOS_KEY")
COSMOS_DB_NAME = os.environ.get("COSMOS_DB_NAME")

PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")
PINECONE_API_ENV=os.environ.get("PINECONE_API_ENV")

TVDB_KEY = os.environ.get("TVDB_KEY")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": None
    }
}

COSMOS_HANDLER = CosmosHandler(COSMOS_KEY,
                               COSMOS_URL,
                               COSMOS_DB_NAME,
                               container_names=['items'])

# TODO: MODEL_DEPLOYMENTS should probably be an environmental variable
# MODEL_DEPLOYMENTS = {
#     'gpt-3.5-turbo': 'gpt-3.5-turbo-1106',  # Azure sometimes uses gpt-35-turbo
#     'gpt-4': 'gpt-4-default-caeast',
#     'text-embedding-ada-002': 'text-embedding-ada-002-caeast'
# }

MODEL_DEPLOYMENTS = {
    'gpt-3.5-turbo': 'gpt-35-turbo-caeast', # Azure sometimes uses gpt-35-turbo
    'gpt-4': 'gpt-4-default-caeast',
    'gpt-4-32k': 'gpt-4-32k-default-caeast',
    'text-embedding-ada-002': 'text-embedding-ada-002-caeast'
}

OAI_HANDLER = OpenAIHandler(
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    MODEL_DEPLOYMENTS
)
CORRECTING_OAI_HANDLER = CorrectingOpenAIHandler(
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    MODEL_DEPLOYMENTS

)
OAI_MODEL=os.environ.get("GPT_35_DEPLOY_NAME")
OPEN_AI_API_KEY=os.environ.get("OPEN_AI_API_KEY")
OAI_HANDLER_BASE=OpenAIHandler(OPEN_AI_API_KEY)

# Make an Azure client we can use for streaming
AZURE_CLIENT = AzureOpenAI(api_key=AZURE_OPENAI_KEY,
                           api_version='2023-05-15',
                           azure_endpoint=AZURE_OPENAI_ENDPOINT)

# Pinecone Configuration
PC_HANDLER = PineconeManager(
    'sa-items-prod',
    PINECONE_API_KEY,
    PINECONE_API_ENV
)

# TVDB Handler Initialization
TVDB_HANDLER = TVDBHandler(TVDB_KEY)

# Open Library Handler
OL_HANDLER = OpenLibraryHandler()
IS_FAST_DEV = str(os.getenv('IS_FAST_DEV')) == "true"

CORS_ALLOWED_ORIGINS = os.environ.get("ENV_CORS_ALLOWED_ORIGINS").split(' ')
CORS_ALLOW_CREDENTIALS = str(os.environ.get("ENV_CORS_ALLOW_CREDENTIALS")) == "true"
CORS_ALLOW_HEADERS = os.environ.get("ENV_CORS_ALLOW_HEADERS").split(' ')
CORS_ALLOW_METHODS = os.environ.get("ENV_CORS_ALLOW_METHODS").split(' ')

CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://redis_db:6388/0")

CSRF_TRUSTED_ORIGINS = os.environ.get("ENV_CSRF_TRUSTED_ORIGINS").split(' ')