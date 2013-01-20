Django CSV Import
=================

Ed Crewe - December 2012

Overview
--------

django-csvimport is a generic importer tool to allow the upload of CSV files for
populating data. The egg installs an admin cvsimport model that has a file upload field.
Add a new csvimport and upload a comma separated values file or MS Excel file.

The upload triggers the import mechanism which matches the header line of the files 
field names to the fields in the selected model. Importing any rows that include all required fields.
Optionally required fields can be specified as part of the upload.
By default duplicate value rows are not inserted.

The import can also be run as a custom command, ie manage.py csvimport filename
for possible use via cronjob etc.

The core import code was based on http://djangosnippets.org/snippets/633/ by Jonathan Holst.
It adds character encoding handling, model field and column autodetection, admin interface,
custom command etc.

NB: There is another similar application django-batchimport but it not packaged,
requires Excel files and doesnt provide a custom command for batch usage.

Installation instructions
-------------------------

Add the following to the INSTALLED_APPS in the settings.py of your project:

>>>  pip install django-csvimport
...
...  INSTALLED_APPS = (
...  ...
...  'csvimport',
...  )
...
...  python manage.py syncdb


Custom command
--------------

Use manage.py csvimport --mappings='' --model='app_label.model_name' importfile.csv

For mappings enter a list of fields in order only if you dont have a header row 
with matching field names - or you want to override it, eg.

--mappings = 'column1=shared_code,column2=org(Organisation|name)'

where (model|foreign key field) is used to specify relations if again, you want to
override what would be looked up from your models.

Admin interface import
----------------------

Just add a csvimport item, fill in the form and submit. 
Failed import rows are added to the log field.

Demonstration installation instructions
---------------------------------------

To see how it works, you can install a demo easily enough eg. via virtual environment, 
then use the tests settings to have some sample models for importing data, and the fixtures are sample csv files.

- Run the following in your shell:

>>> virtualenv mysite
... cd mysite
... pip install django
... pip install django-csvimport
...
... cat > bin/django-admin.py << EOF
... #!/usr/bin/env python
... from django.core import management
... import os
... os.environ["DJANGO_SETTINGS_MODULE"] = "csvimport.tests.settings"
... if __name__ == "__main__":
...     management.execute_from_command_line()
... EOF
...
... django-admin.py syncdb
... django-admin.py runserver

- Go to http://127.0.0.1:8000/admin/ in your browser - pay attention to the trailing / !
- Click on add CSVImport
- Pick the django-csvimport/csvimport/tests/fixtures/countries.csv [1] and upload it
- Check to see if the Country model is now populated.

[1] also available from https://raw.github.com/edcrewe/django-csvimport/master/csvimport/tests/fixtures/countries.csv

Alternatively you can use the command line to upload

django-admin.py csvimport --model='tests.Country' django-csvimport/csvimport/tests/fixtures/countries.csv --settings=csvimport.tests.settings 
 

Acknowledgements
----------------

This egg was created as part of a django dash at the House of Omni, Bristol UK, organised
by Dan Fairs and my local django users group, #DBBUG. It was a core component for an application
for aid agency supply chain sharing, prompted by Fraser Stephens of the HELIOS foundation
and developed by Ed Crewe and Tom Dunham.

 

