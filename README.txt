Django CSV Import
=================

Ed Crewe - July 2011

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

