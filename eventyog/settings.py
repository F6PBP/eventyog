"""
Django settings for eventyog project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()  # Load environment variables from a .env file


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-zob1=r7z=fjniwac*ljo#^o*uiv201#xke*1#4+=m7xxdjx$pv'

PRODUCTION = os.getenv('PROD') == "True"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not PRODUCTION
DEBUG = True

ALLOWED_HOSTS = ['localhost', 'https://eventyog.vercel.app','10.0.2.2', 'eventyog.vercel.app', '127.0.0.1', 'andrew-devito-eventyog.pbp.cs.ui.ac.id', 'https://eventyog.andrew-devito.website', 'eventyog.andrew-devito.website', 'localhost:60502', '*']

CSRF_TRUSTED_ORIGINS=['https://eventyog.andrew-devito.website', 'http://eventyog.andrew-devito.website', 'http://localhost:56509']

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'modules.main',
    'modules.api',
    'modules.authentication',
    'modules.yogpost',
    'modules.cart',
    'modules.merchandise',
    'modules.yogevent',
    'modules.admin_dashboard',
    'modules.yogforum',
    'modules.friends',
    'modules.registered_event',
    'whitenoise.runserver_nostatic',
    'cloudinary',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'eventyog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eventyog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Add these at the top of your settings.py



DATABASES = {}

if not PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': int(os.getenv('DB_PORT')),
        }
    }
    
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#x-auto-field

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Use this for development to serve static files from a directory
]

# Set STATIC_ROOT regardless of the environment
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Set a different folder for production collectstatic

# In production, 'collectstatic' will gather files into STATIC_ROOT folder
    
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# settings.py

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Make sure to adjust the path as needed

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME', 'mxgpapp'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '378869596434125'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', 'RqY1H1Yqi4JysBVrTUaasuIWFes')
)