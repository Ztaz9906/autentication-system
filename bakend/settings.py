"""
Django settings for bakend project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path
from datetime import timedelta
import stripe
from dotenv import load_dotenv
import dj_database_url
# Determinar si estamos en Vercel
IN_VERCEL = os.environ.get('VERCEL_ENV') is not None

# Cargar variables de entorno solo si no estamos en Vercel
if not IN_VERCEL:
    ENV_FILE = '.env'
    load_dotenv(ENV_FILE)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ib20h(eg8u^ry!u+v8n&(r6w&v*bed6)f7aw7sg%h5)qa-x(y4')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Configuración de CORS
ALLOWED_HOSTS: list[str] = os.getenv("ALLOWED_HOSTS", "").split(";")
#ALLOWED_HOSTS = ['el-chuletazo-439c3c79d05b.herokuapp.com']
CORS_ALLOWED_ORIGINS: list[str] = os.getenv("CORS_ALLOWED_ORIGINS", "").split(";")
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'rest_framework_simplejwt.token_blacklist',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    "django_filters",
    "drf_spectacular",
    'documentacion',
    'authenticacion',
    'nomencladores.apps.NomencladoresConfig',
    'tienda'
]
AUTH_USER_MODEL = 'authenticacion.Usuario'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'bakend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'authenticacion/templates')],
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

WSGI_APPLICATION = 'bakend.wsgi.app'

AUTHENTICATION_BACKENDS = [
    'authenticacion.auth.EmailOrUsernameModelBackend',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    "TITLE": "EL Chuletazo API",
    "DESCRIPTION": "Breve documentación asociada al API de EL Chuletazo.",
    "VERSION": "1.0.0",
    "CONTACT": {
        "email": "elchuletazo@gmail.com",
    },
    'LICENSE': {
        'name': 'Terms of Use',
    },
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_INCLUDE_SCHEMA": False,
    # deepLinking: true habilita la actualización de los fragmentos de url con links profundos en tags y operaciones
    # urls es un arreglo de urls que apuntan a objetos que definen la API (schema).
    # Layout es el nombre del componente disponible vía plugin que servirá como interfaz del swagger al máximo nivel.
    # Filter habilita la opción de filtrar los endpoints por tag en el swagger.
    "SWAGGER_UI_SETTINGS": """{
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        layout: "StandaloneLayout",
        filter: true
    }""",
}

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': "access_token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",
    "JWT_AUTH_HTTPONLY": False,
    'USER_DETAILS_SERIALIZER': 'authenticacion.api.serializers.users.auth.SerializadorUsuarioAuth',
    'OLD_PASSWORD_FIELD_ENABLED': True,
    'PASSWORD_RESET_SERIALIZER': 'authenticacion.api.serializers.auth.password.reset.CustomPasswordResetSerializer'
}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# OAuth Google

SOCIALACCOUNT_PROVIDERS = {
    'google': {
         "APPS": [
            {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "secret": os.getenv('GOOGLE_CLIENT_SECRET'),
            },
        ],
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'VERIFIED_EMAIL': True,
        'EMAIL_AUTHENTICATION': True
    }
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Configuracion de servidor SMTP para enviar correos
# Django defaults to this backend, but if you'd like to be explicit:

# Configuración de email para desarrollo
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST','mail.smtp2go.com')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER','estudiantes.uci.cu')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD','KoxeCSdDtVLtMc8g')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL",'ztazhorde@gmail.com')
SITE_URL = os.getenv("SITE_URL", "http://loacalhost:3000") # La URL base de tu sitio

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}



# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = (BASE_DIR / "apps/documentacion/locale",)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_DIRS = [BASE_DIR / 'static', ]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_HOST = os.getenv("DJANGO_STATIC_HOST", "")

STATIC_URL = STATIC_HOST + "/static/"

MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = STATIC_HOST + "/media/"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51PQbzPGkiwqRm16CSYV3zip8aDpQd6HYR6xagymesVarWWOh9BiMS8PraFFI5STwxv0wwmomqxpSI2a3hG5khhLt00cboMxa7Z')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_maFNLc45V6HVLCS013lCxHG6r8DoIWqn')
stripe.api_key = STRIPE_SECRET_KEY
