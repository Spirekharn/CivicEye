"""
CivicEye – Django Settings
config/settings.py
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'civiceye-dev-key-change-before-production-2026-group02-local-only',
)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in {'1', 'true', 'yes', 'on'}
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'DJANGO_ALLOWED_HOSTS',
        '*' if DEBUG else 'localhost,127.0.0.1,[::1]',
    ).split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'complaints',
    'departments',
    'finance',
    'notifications',
    'analytics',
    # 'assignments' — reserved for Phase 2 expansion; no active models
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'config.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CITY_CORP_HOTLINES = {
    'DNCC': {
        'name': 'Dhaka North City Corporation',
        'shortcode': '16106',
        'numbers': ['09602222333', '09602222334'],
        'emergency': '999',
    },
    'DSCC': {
        'name': 'Dhaka South City Corporation',
        'shortcode': '333',
        'numbers': ['02-9559765', '02-9559764'],
        'emergency': '999',
    },
    'CCC': {
        'name': 'Chattogram City Corporation',
        'shortcode': '16579',
        'numbers': ['031-630024', '031-630025'],
        'emergency': '999',
    },
    'SCC': {
        'name': 'Sylhet City Corporation',
        'shortcode': '333',
        'numbers': ['0821-716000'],
        'emergency': '999',
    },
    'RCC': {
        'name': 'Rajshahi City Corporation',
        'shortcode': '333',
        'numbers': ['0721-772211'],
        'emergency': '999',
    },
    'KCC': {
        'name': 'Khulna City Corporation',
        'shortcode': '333',
        'numbers': ['041-761064'],
        'emergency': '999',
    },
    'BCC': {
        'name': 'Barishal City Corporation',
        'shortcode': '333',
        'numbers': ['0431-64400'],
        'emergency': '999',
    },
    'NCC': {
        'name': 'Narayanganj City Corporation',
        'shortcode': '333',
        'numbers': ['02-7640860'],
        'emergency': '999',
    },
    'GCC': {
        'name': 'Gazipur City Corporation',
        'shortcode': '333',
        'numbers': ['02-9801000'],
        'emergency': '999',
    },
    'MCC': {
        'name': 'Mymensingh City Corporation',
        'shortcode': '333',
        'numbers': ['091-66000'],
        'emergency': '999',
    },
    'COCC': {
        'name': 'Cumilla City Corporation',
        'shortcode': '333',
        'numbers': ['081-72000'],
        'emergency': '999',
    },
    'RNCC': {
        'name': 'Rangpur City Corporation',
        'shortcode': '333',
        'numbers': ['0521-62020'],
        'emergency': '999',
    },
    'default': {
        'name': 'National Helpline',
        'shortcode': '333',
        'numbers': [],
        'emergency': '999',
    },
}

# email — console backend for dev, swap host/port/user/pass for production smtp
EMAIL_BACKEND   = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@civiceye.bd'

# ---------------------------------------------------------------------------
# FUTURE EXTERNAL AUTHORITY ROUTING
# When Bangladesh utility authorities expose APIs or require direct routing,
# add entries here. Each authority declares the complaint categories it handles
# and the city corporations it covers. The complaints.location_router module
# can be extended to check this dict before falling back to department routing.
#
# FUTURE_AUTHORITIES = {
#     'DESCO': {
#         'name': 'Dhaka Electric Supply Company',
#         'handles': ['electricity'],
#         'area': ['DNCC', 'DSCC'],
#         'api_endpoint': None,
#     },
#     'DPDC': {
#         'name': 'Dhaka Power Distribution Company',
#         'handles': ['electricity'],
#         'area': ['DSCC'],
#         'api_endpoint': None,
#     },
#     'WASA': {
#         'name': 'Water Supply & Sewerage Authority',
#         'handles': ['water', 'environment'],
#         'area': ['DNCC', 'DSCC'],
#         'api_endpoint': None,
#     },
#     'TGCL': {
#         'name': 'Titas Gas Transmission & Distribution Company',
#         'handles': ['fire'],
#         'area': ['nationwide'],
#         'api_endpoint': None,
#     },
# }
# ---------------------------------------------------------------------------

if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() in {'1', 'true', 'yes', 'on'}
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
