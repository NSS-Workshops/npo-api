from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-x9yg09-pv69(#mz@!n(1&c_rxvks#3*v&#vx!%t39p(n(f0gbb"
)

DEBUG = True

APPEND_SLASH = False

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Remove allauth apps
    "npoapi",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_extensions",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Default authentication backend
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS configuration
CORS_ALLOW_CREDENTIALS = True  # Allow credentials to be included in requests

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Your Next.js frontend URL
    "http://127.0.0.1:3000",  # Additional variations if needed
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",  # If you're using this for testing with Postman
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",  # Your Next.js frontend URL
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

ROOT_URLCONF = "npoproject.urls"

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

WSGI_APPLICATION = "npoproject.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "auth.user"  # Use the custom user model

# Password validation
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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# GitHub OAuth credentials loaded from the .env file
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "Ov23liX9qowoyyanQJnw")
GITHUB_CLIENT_SECRET = os.getenv(
    "GITHUB_CLIENT_SECRET", "262514825d1995a44c00d3aadeeb3a5f7d6c5bc4"
)
GITHUB_REDIRECT_URI = "http://localhost:8000/github/callback/"  # Must match the callback URL registered in GitHub OAuth App

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
