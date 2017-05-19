echo "Test shell script for running the shell command to import a CSV file and then check it worked by using commandline sqlite3"
echo "Run from the root of your django install"
rm src/django-csvimport/db.sqlite3
bin/django-admin.py migrate --settings='csvimport.settings'
bin/django-admin.py importcsv --settings='csvimport.settings' --model='csvimport.Country' src/django-csvimport/csvimport/tests/fixtures/countries.csv
sqlite3 src/django-csvimport/db.sqlite3 "select * from csvtests_country"
echo "Run test suite"
bin/django-admin.py test --settings='csvimport.settings' csvimport.tests
