Tests Readme
============

Test files are imported via the __init__.py 

>>> from foobar_tests import *

For one off run of tests use 

>>> manage.py test --settings='csvimport.settings' csvimport.tests

Or could use following import of settings for manage.py / django-admin.py ...

>>> #!/bin/python
>>> from django.core import management
>>> import os
>>> os.environ['DJANGO_SETTINGS_MODULE'] = 'csvimport.settings'
>>>
>>>
>>> if __name__ == "__main__":
>>>    management.execute_from_command_line()

Then can run via 

>>> manage.py test csvimport.tests
