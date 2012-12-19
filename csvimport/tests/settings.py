# Settings to be used when running unit tests
# python manage.py test --settings=django-csvimport.tests.settings django-csvimport
import os

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django-csvimport-test.db',
        'USER': '',     # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '',     # Set to empty string for localhost. 
        'PORT': '',     # Set to empty string for default. 
    }
}
# If not set or CSVIMPORT = 'screen' then it only sends loglines to Admin UI display
CSVIMPORT_LOG = 'logger'
# Turn on logger usage and log to a text file to check for in tests ...
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), 
                                          'csvimport_test.log')
        },
    },
   'loggers': {
        'csvimport': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
MEDIA_ROOT = ''
MEDIA_URL = '/files/'
# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

INSTALLED_APPS = (
    # Add csvimport app itself and the tests models
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'csvimport',
    'csvimport.tests'
)
SITE_ID = 1

# This merely needs to be present - as long as your test case specifies a
# urls attribute, it does not need to be populated.
ROOT_URLCONF = 'csvimport.tests.urls'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't_8)4w_csvimport_not_secret_test_key_7^b*s%w$zrud'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# For CI testing of releases
try:
    import django_jenkins
    CI = True
except:
    CI = False

if CI:
    INSTALLED_APPS += ('django_jenkins',)
    PROJECT_APPS = ('csvimport',)
    JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                     'django_jenkins.tasks.with_coverage',
                     'django_jenkins.tasks.django_tests',)
