# Settings to be used when running unit tests
# ./bin/django-admin test --settings=csvimport.settings csvimport.tests

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "(2^xk$^us_v$zd-qhd1_z8a!89*cc415b(*%*o(med4bk^w3ui"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ALLOWED_HOSTS = []

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # insert your TEMPLATE_DIRS here
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "csvimport.app.CSVImportConf",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

SITE_ID = 1

# This merely needs to be present - as long as your test case specifies a
# urls attribute, it does not need to be populated.
ROOT_URLCONF = "csvimport.tests.urls"

WSGI_APPLICATION = "csvimport.wsgi.application"

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = "/static/"


# If not set or CSVIMPORT = 'screen' then it only sends loglines to Admin UI display
CSVIMPORT_LOG = "logger"
# Turn on logger usage and log to a text file to check for in tests ...
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "logfile": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": os.path.join(os.path.dirname(__file__), "csvimport_test.log"),
        }
    },
    "loggers": {
        "csvimport": {"handlers": ["logfile"], "level": "DEBUG", "propagate": False}
    },
}

TEST_RUNNER = "csvimport.tests.testrunner.CSVImportRunner"
MIGRATION_MODULES = {"csvimport": "csvimport.tests.migrations"}
