# Make our own testrunner that by default only tests our own apps
import shutil
from django.conf import settings
from django.test.runner import DiscoverRunner


class CSVImportRunner(DiscoverRunner):
    def setup_databases(self, *args, **kwargs):
        print("Add the csvimport test models migrations")
        settings.MIGRATION_MODULES["csvimport"] = "csvimport.tests.migrations"
        return super(CSVImportRunner, self).setup_databases(*args, **kwargs)
