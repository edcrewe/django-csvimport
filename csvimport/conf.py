from appconf import AppConf
from django.conf import settings


class CSVImportConf(AppConf):
    MODELS = []
    MEDIA_ROOT = settings.MEDIA_ROOT
