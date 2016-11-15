import os
from django.apps import AppConfig
from django.conf import settings


class CSVImportConf(AppConfig):
    name = 'csvimport'
    verbose_name = 'CSV importer'
    MODELS = ['csvimport.models']
    MEDIA_ROOT = settings.MEDIA_ROOT
    path = os.path.dirname(os.path.abspath(__file__))
