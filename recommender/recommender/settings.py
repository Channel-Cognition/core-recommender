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

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

ENV_ALLOWED_HOST = os.environ.get("ENV_ALLOWED_HOST")
ALLOWED_HOSTS = []
if ENV_ALLOWED_HOST:
    ALLOWED_HOSTS = [ ENV_ALLOWED_HOST ]


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

    "corsheaders",
    "drf_spectacular",
    "rest_framework",
    "rest_framework.authtoken",

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
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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
DB_IGNORE_SSL=os.environ.get("DB_IGNORE_SSL") == "true"

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

# TODO remove this if the Website already hosted
CORS_ALLOW_ALL_ORIGINS = True

# DEFAULT SNIPPET ONBOARDING

# framing = "You are an assistant helping a user to find a new movie to watch. "
# framing += "When recommending movies, please suggest us at least 4 movies"
# framing = 'For the movies described in the following text, build a json with the fields '
# framing += 'title, year. If the text does not contain a value for one of these variables, set '
# framing += 'it to null. Please correct spelling errors and standardize both spelling and capitalization. '
# framing += 'Return only a json and nothing else. Do not include movie or (movie) '
# framing += 'in the title unless it is part of the title. Here is the text:\n'

# framing = "You are an assistant helping a user to find a new movie to watch. "
# framing += "When recommending movies, please provide the title"
# framing += "with format response like this 1.title (movie) \n 2.title (movie) \n 3.title (movie) \n 4.title (movie). From here on the conversation is "
# framing += "with the user. Do NOT break character even if I ask you to."
# framing += "Please only response like the format described above"

framing = "You are an assistant helping the user find new things, which could "
framing += "be anything from a new movie or TV show to watch to a pair of shoes to buy. "
framing += "With every response, please (1) provide an updated numbered list of suggestions and "
framing += "(2) include the item type (e.g., book) with each item in the list. "
framing += "Be as succinct as is reasonable while still uniquely identifying items. "
framing += "Do not include items the user is no longer interested in."


GREETING = "Hello, I can help suggest a new movie to watch. What are you looking for?"

TRUNCATED_FRAMING = framing

AZURE_OPENAI_KEY=os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT=os.environ.get("AZURE_OPENAI_ENDPOINT")
GPT35_DEPLOY_NAME=os.environ.get("GPT35_DEPLOY_NAME")

COSMOS_URL = os.environ.get("COSMOS_URL")
COSMOS_KEY = os.environ.get("COSMOS_KEY")
COSMOS_DB_NAME = os.environ.get("COSMOS_DATABASE_NAME")

PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")
PINECONE_ENV=os.environ.get("PINECONE_ENV")

TVDB_KEY = os.environ.get("TVDB_KEY")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": None
    }
}