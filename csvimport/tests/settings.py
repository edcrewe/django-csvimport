# Settings to be used when running unit tests
# python manage.py test --settings=django-csvimport.tests.settings django-csvimport

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/django-csvimport-test.db',
        'USER': '',     # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '',     # Set to empty string for localhost. 
        'PORT': '',     # Set to empty string for default. 
    }
}

MEDIA_ROOT = '/tmp'
MEDIA_URL = '/files/'

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
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
