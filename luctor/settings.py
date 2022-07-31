"""
Django settings for luctor project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LOGIN_REDIRECT_URL='/user/'

# Paths to store database and uploaded files
# for production, should move uploads somewhere suitable for serving
DATA_DIR = os.path.join(BASE_DIR, "data")
MEDIA_ROOT = os.path.join(DATA_DIR, "upload", "")
MEDIA_URL = "/media/"

FILE_UPLOAD_PERMISSIONS = 0o644

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-z$%!6hq(wt@4r%l3qp7!5fl776*-mk_qi43m%(c=x&m6$c=(h'

# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = ['kookboot.com', 'kookles.vanatteveldt.com', 'localhost']
if os.environ.get("DEBUG"):
    DEBUG = os.environ.get('DEBUG', 'N') == 'Y'
else:
    import sys
    DEBUG = "manage.py" in sys.argv[0]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'vrnmbdhomztljcbk'#os.environ['GMAIL_PASSWORD'].strip()
EMAIL_HOST_USER = 'vanatteveldt@gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL  = 'vanatteveldt@gmail.com'

LOGIN_URL = "login"

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_elasticsearch_dsl',
    'recipes',
    'widget_tweaks'
)

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'luctor.urls'

WSGI_APPLICATION = 'luctor.wsgi.application'

ES_URL = os.environ.get("LUCTOR_ES_URL", 'localhost:9200')

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ES_URL
    },
}

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT, 'static')

DATE_FORMAT = 'j F Y'

LANGUAGE_CODE = 'nl-NL'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s %(module)s %(levelname)s] %(message)s'
        },
    },
}

if DEBUG:
    LOGGING['loggers'] = {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'elasticsearch': {'level': 'INFO'}
    }

else:
    LOGGING['handlers']['file'] = {
        'class': 'logging.FileHandler',
        'filename': 'luctor.log',
        'formatter': 'verbose',
    }
    LOGGING['loggers'] = {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'luctor': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
    
