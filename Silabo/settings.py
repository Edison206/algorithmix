"""Django settings para Silabo (ALGORITHMIX). Funciona en local y en PythonAnywhere."""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

USUARIO_PA = 'edison206'
EN_PRODUCCION = ('PYTHONANYWHERE_DOMAIN' in os.environ
                 or str(BASE_DIR).startswith(f'/home/{USUARIO_PA}'))

_debug_env = os.environ.get('DJANGO_DEBUG')
if _debug_env is not None:
    DEBUG = _debug_env.strip().lower() in ('1', 'true', 'yes', 'si')
else:
    DEBUG = not EN_PRODUCCION

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-%dg#f=rz0zdioo$@fzs*+b$dz30x-w%^#08jy86hbvrao_y)qk'
)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', f'{USUARIO_PA}.pythonanywhere.com']
CSRF_TRUSTED_ORIGINS = [f'https://{USUARIO_PA}.pythonanywhere.com']

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    # No usar SECURE_SSL_REDIRECT: en PythonAnywhere causa bucles. Usar "Force HTTPS".

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'estudiantes',
]

AUTH_USER_MODEL = 'estudiantes.Usuario'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Silabo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Silabo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/bienvenida/'
LOGOUT_REDIRECT_URL = '/login/'

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO'},
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
    },
}
