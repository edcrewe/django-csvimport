from django.http import HttpResponse


def index(request, template='README.txt', **kwargs):
    return HttpResponse ('''<html><body><h1>django-csvimport Test app</h1>
                  <p>You have installed the test django-csvimport
                  application. Click on the <a href="/admin/">admin</a>
                  to try it</p>
                  <p>NB: you must run<br />
                     django-admin.py migrate --settings=csvimport.settings <br />
                  first to create the test models.
                  <p>Click on csvimport in the admin</p>
                  <p>Try importing data via the test csv files in
                     django-csvimport/csvimport/tests/fixtures folder</p>
                  <p>Click on Add csvimport</p>
                  <p>For example select Models name: tests.Country and upload the countries.csv file</p>
                  </body></html>''')
