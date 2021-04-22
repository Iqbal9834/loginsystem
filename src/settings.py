"""
Django settings for src prosject.

Generated by 'django-admin startproject' using Django 2.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ
from datetime import timedelta

# from datetime import datetime

env = environ.Env()

BASE_DIR = os.path.dirname(__file__)
BASE_ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir, os.pardir))

# Load environ file .env
env_file_path = os.path.join(BASE_ROOT_DIR, ".env")
env.read_env(env_file_path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

DEFAULT_SECRET_KEY = "@#$rgdfgdghFGH_W%#$%+4w5sdrwerw__fg"

SECRET_KEY = '8lu*6g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # "django.contrib.admin",
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "rest_framework_swagger",
    "corsheaders",
    # apps
    "src.apis",
]

MIDDLEWARE = [
    # customs
    "src.apis.middleware.request_context.RequestContextMiddleware",
    "src.apis.middleware.request_id.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "src.apis.middleware.authentication.JWTAuthenticationMiddleware",
    "src.apis.middleware.authentication.JWTValidationMiddleware",
    "src.apis.middleware.user.UserActiveMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTH_TOKEN_EXPIRATION = env.int("AUTH_TOKEN_EXPIRATION", default=99999)

# refresh token expire time default to 1 week
REFRESH_TOKEN_EXPIRATION = env.int("REFRESH_TOKEN_EXPIRATION_MINUTES", default=10076)
JWT_AUTH = {
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_EXPIRATION_DELTA": timedelta(seconds=AUTH_TOKEN_EXPIRATION),
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_VERIFY": True,
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_ALLOW_REFRESH": True,
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(seconds=REFRESH_TOKEN_EXPIRATION),
    "JWT_AUTH_COOKIE": "token",
}


ROOT_URLCONF = "src.urls"


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

WSGI_APPLICATION = "src.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# user auth mode
AUTH_USER_MODEL = "apis.User"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("src.apis.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # We are not using here JSONWebTokenAuthentication
        # authentication class, as we are already using
        # `JWTAuthenticationMiddleware` in django middleware for
        # support `request.user` in other following middleware's
        # "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # For authentication via  API keys
        "src.apis.middleware.authentication.ApiKeyAuthentication",
    ),
    "NON_FIELD_ERRORS_KEY": "_generic_errors",
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    # It's set as- Number of requests/Period, where period should be
    # one of: ('s', 'sec', 'm', 'min', 'h', 'hour', 'd', 'day')
    "DEFAULT_THROTTLE_CLASSES": [
        # "oneupvision.apis.throttles.BurstAnonRateThrottle"
        "src.apis.utils.throttels.BurstAnonRateThrottle"
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon_burst": "60/min",
        "user_signup_fail": "10/min",
        "login_bad_attempt": "10/min",
        "login_otp_success": "10/min",
        "verify_email_fail": "10/min",
        "reset_password_fail": "10/min",
        "reset_password_email_success": "10/min",
    },
}


# -------------------  Swagger Schema settings ---------------------------
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {"basic": {"type": "apiKey"}},
    "LOGIN_URL": "admin:login",
    "LOGOUT_URL": "admin:logout",
}
# To disable swagger schema, set empty string url path
SWAGGER_SCHEMA_URL_PATH = env("SWAGGER_SCHEMA_URL_PATH", default="_swagger-schema/")

APP_USER_VERIFY_EMAIL_URL_PATH = env("APP_USER_VERIFY_EMAIL_URL_PATH", default=None)
APP_USER_RESET_PASSWORD_URL_PATH = env("APP_USER_RESET_PASSWORD_URL_PATH", default=None)
# APP_ROOT_URL = env("APP_ROOT_URL", default="http://localhost")

# -------------------------- email configration---------------------------------
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
EMAIL_PORT = env.str("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# ----------------------------Mobile Serivce ------------------------------------
AUTH_KEY = env("AUTH_KEY", default=None)
COUNTRY_CODE = env("COUNTRY_CODE", default="91")
# ------------------ CORS Middleware settings -----------------------------
default_headers = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-site-id",
    "x-site-version",
    "x-access-token",
]
