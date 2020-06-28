import os
from django.apps import AppConfig
from django.conf import settings

"""The csvimport tool uses two models for the admin interface
   The tests also have models ... the runner copies in their migrations 
   If new test models are added, edit MODELS to add csvimport.tests.models and run
   makemigrations csvimport - then move the generated migration file to tests/migrations
"""


class CSVImportConf(AppConfig):
    name = "csvimport"
    verbose_name = "CSV importer"
    MODELS = ["csvimport.models"]
    MEDIA_ROOT = settings.MEDIA_ROOT
    path = os.path.dirname(os.path.abspath(__file__))
