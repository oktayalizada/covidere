"""
Django settings for shoplokalt project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import datetime
import os
import requests

from django.utils.translation import gettext_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# If deployment is in ECS
ALLOWED_HOSTS_ECS = os.environ.get('ALLOWED_HOSTS_ECS', False)
if ALLOWED_HOSTS_ECS:
    try:
        metadata = requests.get('http://169.254.170.2/v2/metadata',
                                timeout=0.1).json()
        ip = metadata['Containers'][0]['Networks'][0]['IPv4Addresses'][0]
        ALLOWED_HOSTS = ['.elb.amazonaws.com', ip,'foodbee.dk']
    except requests.exceptions.ConnectionError:
        pass
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Geolocation
    'django.contrib.gis',
    # Own apps
    'base.apps.BaseConfig',
    'basket.apps.BasketConfig',
    'order.apps.OrderConfig',
    'product.apps.ProductConfig',
    'postcode.apps.PostcodeConfig',
    'shop.apps.ShopConfig',
    # Form helper
    'crispy_forms',
    # Extra fields
    'stdimage',
    'phonenumber_field',
    # Security
    'axes',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'shoplokalt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'base.processors.basket_counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'shoplokalt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators


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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'da-DK'
LANGUAGES = [
    ('da', gettext_lazy('Danish')),
    ('en', gettext_lazy('English')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
S3 = os.getenv('USE_S3') == 'TRUE'
if S3:
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'shoplokalt')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.eu-north-1.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    STATICFILES_LOCATION = 'static'
    MEDIAFILES_LOCATION = 'media'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)
    MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    STATICFILES_DIRS = []
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    MEDIA_URL = '/media/'


AUTH_USER_MODEL = 'base.User'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = '/shopadmin/'

LOGIN_URL = '/users/login/'

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
DEFAULT_FROM_EMAIL = 'no-reply@foodbee.dk'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API', 'anything')

LOGOUT_REDIRECT_URL = '/'

PHONENUMBER_DEFAULT_REGION = 'DK'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "shoplokalt/locale"),
]

AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'axes.backends.AxesBackend',

    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]

AXES_COOLOFF_TIME = datetime.timedelta(minutes=5)
AXES_LOCKOUT_URL = '/users/locked_out/'
AXES_LOCKOUT_TEMPLATE = 'registration/locked_out.html'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

try:
    from shoplokalt.settings_local import *  # noqa: F401,F403
except ModuleNotFoundError:
    pass
