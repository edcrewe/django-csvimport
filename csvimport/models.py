from django.db import models
from csvimport.conf import settings
from copy import deepcopy
from django.core.files.storage import FileSystemStorage
import re

fs = FileSystemStorage(location=settings.MEDIA_ROOT)
CHOICES = (('manual', 'manual'), ('cronjob', 'cronjob'))

# Create your models here.
if not settings.CSVIMPORT_MODELS:
    MODELS = ['%s.%s' % (m._meta.app_label,
                         m.__name__) for m in models.loading.get_models()
                         if m._meta.app_label != 'contenttypes']
else:
    MODELS = deepcopy(settings.CSVIMPORT_MODELS)

MODELS = tuple([(m, m) for m in MODELS])


class CSVImport(models.Model):
    """ Logging model for importing files """
    model_name = models.CharField(max_length=255, blank=False,
                                  default='iisharing.Item',
                                  help_text='Please specify the app_label.model_name',
                                  choices=MODELS)
    field_list = models.CharField(max_length=255, blank=True,
                        help_text='''Enter list of fields in order only if
                                     you dont have a header row with matching field names, eg.
                                     "column1=shared_code,column2=org(Organisation|name)"''')
    upload_file = models.FileField(upload_to='csv', storage=fs)
    file_name = models.CharField(max_length=255, blank=True)
    encoding = models.CharField(max_length=32, blank=True)
    upload_method = models.CharField(blank=False, max_length=50,
                                     default='manual', choices=CHOICES)
    error_log = models.TextField(help_text='Each line is an import error')
    import_date = models.DateField(auto_now=True)
    import_user = models.CharField(max_length=255, default='anonymous',
                                   help_text='User id as text', blank=True)

    def error_log_html(self):
        return re.sub('\n', '<br/>', self.error_log)
    error_log_html.allow_tags = True

    def __unicode__(self):
        return self.upload_file.name


class ImportModel(models.Model):
    """ Optional one to one mapper of import file to Model """
    csvimport = models.ForeignKey(CSVImport)
    numeric_id = models.PositiveIntegerField()
    natural_key = models.CharField(max_length=100)
