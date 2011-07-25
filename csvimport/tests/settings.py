# Settings to be used when running unit tests
# python manage.py test --settings=django-csvimport.tests.settings django-csvimport


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

INSTALLED_APPS = (
    # Add csvimport app itself and the tests models
    'csvimport',
    'tests'
)
SITE_ID = 1

# This merely needs to be present - as long as your test case specifies a
# urls attribute, it does not need to be populated.
ROOT_URLCONF = ''
