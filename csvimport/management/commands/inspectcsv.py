""" Developed for www.heliosfoundation.org by Ed Crewe and Tom Dunham
    Django command to import CSV files
"""
import re
import django
from distutils.version import StrictVersion

from optparse import make_option
from django.core.management.base import LabelCommand, BaseCommand

# from csvimport import CSVParser

cleancol = re.compile('[^0-9a-zA-Z]+')  # cleancol.sub('_', s)

from csvimport.parser import CSVParser


class Command(LabelCommand, CSVParser):
    """
    Inspect a CSV resource to generate the code for a Django model.
    """

    make_options = (
        make_option('--defaults', default='',
                    help='''Provide comma separated defaults for the import
                                       (field1=value,field3=value, ...)'''),
        make_option('--model', default='',
                    help='Please provide the model to import to'),
        make_option('--charset', default='',
                    help='Force the charset conversion used rather than detect it')
    )

    # Adding support for Django 1.10+
    if StrictVersion(django.get_version()) >= StrictVersion('1.10.0'):
        option_list = getattr(BaseCommand, 'option_list', ()) + make_options
    else:
        option_list = BaseCommand.option_list + make_options

    help = "Analyses CSV file date to generate a Django model"

    def __init__(self):
        """ Set default attributes data types """
        super(Command, self).__init__()
        self.csvfile = []
        self.charset = ''
        self.filehandle = None
        self.makemodel = ''
        self.errors = []

    def handle_label(self, label, **options):
        """ Handle the circular reference by passing the nested
            save_csvimport function
        """
        csvfile = label
        defaults = options.get('defaults', [])
        model = options.get('model', '')
        charset = options.get('charset', '')
        self.defaults = self.set_mappings(defaults)
        self.check_filesystem(csvfile)
        if model.find('.') > -1:
            app_label, model = model.split('.')
        else:
            app_label = 'csvimport'

        model_definition = self.create_new_model(model, app_label)
        if self.errors:
            print (self.errors)
            return

        self.makemodel = '""" A django model generated with django-csvimport csvinspect\n'
        self.makemodel += '    which used OKN messytables to guess data types - may need some manual tweaks!\n"""'
        self.makemodel += '\nfrom django.db import models\n\n'
        self.makemodel += model_definition
        print (self.makemodel)
        return

    def create_new_model(self, modelname, app_label):
        """ Use messytables to guess field types and build a new model """

        nocols = False
        cols = self.csvfile[0]
        for col in cols:
            if not col:
                nocols = True
        if nocols:
            cols = ['col_%s' % num for num in range(1, len(cols))]
            print ('No column names for %s columns' % len(cols))
        else:
            cols = [cleancol.sub('_', col).lower() for col in cols]
        try:
            from messytables import any_tableset, type_guess
        except:
            self.errors.append(
                'If you want to inspect CSV files to generate model code, you must install https://messytables.readthedocs.org')
            self.modelname = ''
            return

        try:
            table_set = any_tableset(self.filehandle)
            row_set = table_set.tables[0]
            types = type_guess(row_set.sample)
            types = [str(typeobj) for typeobj in types]
        except Exception as err:
            self.errors.append('messytables could not run due to error')
            self.errors.append(str(err))
            self.modelname = ''
            return

        fieldset = []
        maximums = self.get_maxlengths(cols)
        for i, col in enumerate(cols):
            length = maximums[i]
            if types[i] == 'String' and length > 255:
                types[i] = 'Text'
            integer = length
            decimal = int(length / 2)
            if decimal > 10:
                decimal = 10
            blank = True
            default = True
            column = (col, types[i], length, length, integer, decimal, blank, default)
            fieldset.append(column)
        # Import here so that messytables is not a dependency for just using csvimport cmd
        from csvimport.make_model import MakeModel
        maker = MakeModel()
        return maker.model_from_table('%s_%s' % (app_label, modelname), fieldset)

    def get_maxlengths(self, cols):
        """ Get maximum column length values to avoid truncation
            -- can always manually reduce size of fields after auto model creation
        """
        maximums = [0] * len(cols)
        for line in self.csvfile[1:100]:
            for i, value in enumerate(line):
                if value and len(value) > maximums[i]:
                    maximums[i] = len(value)
                if maximums[i] > 10:
                    maximums[i] += 10
                if not maximums[i]:
                    maximums[i] = 10
        return maximums
