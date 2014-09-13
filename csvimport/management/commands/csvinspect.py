""" Developed for www.heliosfoundation.org by Ed Crewe and Tom Dunham 
    Django command to import CSV files
"""
import os, csv, re
import codecs
import chardet

from django.core.management.base import LabelCommand, BaseCommand
from optparse import make_option

cleancol = re.compile('[^0-9a-zA-Z]+')  # cleancol.sub('_', s)

class CSVParser(object):
    """ Open a CSV file, check its encoding and parse it into memory 
        and set up the map of the fields
    """

    csvfile = []
    charset = ''
    filehandle = None

    def __csvfile(self, datafile):
        """ Detect file encoding and open appropriately """
        self.filehandle = open(datafile)
        if not self.charset:
            diagnose = chardet.detect(self.filehandle.read())
            self.charset = diagnose['encoding']
        try:
            csvfile = codecs.open(datafile, 'r', self.charset)
        except IOError:
            self.error('Could not open specified csv file, %s, or it does not exist' % datafile, 0)
        else:
            # CSV Reader returns an iterable, but as we possibly need to
            # perform list commands and since list is an acceptable iterable,
            # we'll just transform it.
            try:
                return list(self.charset_csv_reader(csv_data=csvfile,
                                                charset=self.charset))
            except:
                output = []
                count = 0
                # Sometimes encoding is too mashed to be able to open the file as text
                # so reopen as raw unencoded and just try and get lines out one by one
                # Assumes "," \r\n delimiters
                try:
                    with open(datafile, 'rb') as content_file:
                        content = content_file.read()
                    if content:
                        rows = content.split('\r\n')
                        for row in rows:
                            rowlist = row[1:-1].split('","')
                            if row:
                                count += 1
                                try:
                                    output.append(rowlist)
                                except:
                                    self.loglist.append('Failed to parse row %s' % count)
                except:
                    self.loglist.append('Failed to open file %s' % datafile)
                return output

    def charset_csv_reader(self, csv_data, dialect=csv.excel,
                           charset='utf-8', **kwargs):
        csv_reader = csv.reader(self.charset_encoder(csv_data, charset),
                                dialect=dialect, **kwargs)
        for row in csv_reader:
            # decode charset back to Unicode, cell by cell:
            yield [unicode(cell, charset) for cell in row]

    def charset_encoder(self, csv_data, charset='utf-8'):
        """ Check passed a valid charset then encode """
        test_string = 'test_real_charset'
        try:
            test_string.encode(charset)
        except:
            charset = 'utf-8'
        for line in csv_data:
            yield line.encode(charset)

    def set_mappings(self, mappings):
        """
        Parse the mappings, and return a list of them.
        """
        if not mappings:
            return []

        def parse_mapping(args):
            """
            Parse the custom mapping syntax (column1=field1(ForeignKey|field),
            etc.)

            >>> parse_mapping('a=b(c|d)')
            [('a', 'b', '(c|d)')]
            """
            # value = word or date format match
            pattern = re.compile(r'(\w+)=(\d+/\d+/\d+|\d+-\d+-\d+|\w+)(\(\w+\|\w+\))?')
            mappings = pattern.findall(args)

            mappings = list(mappings)
            for mapping in mappings:
                mapp = mappings.index(mapping)
                mappings[mapp] = list(mappings[mapp])
                mappings[mapp][2] = parse_foreignkey(mapping[2])
                mappings[mapp] = tuple(mappings[mapp])
            mappings = list(mappings)
            
            return mappings

        def parse_foreignkey(key):
            """
            Parse the foreignkey syntax (Key|field)

            >>> parse_foreignkey('(a|b)')
            ('a', 'b')
            """

            pattern = re.compile(r'(\w+)\|(\w+)', re.U)
            if key.startswith('(') and key.endswith(')'):
                key = key[1:-1]

            found = pattern.search(key)

            if found != None:
                return (found.group(1), found.group(2))
            else:
                return None

        mappings = mappings.replace(',', ' ')
        mappings = mappings.replace('column', '')
        return parse_mapping(mappings)


    def check_filesystem(self, csvfile):
        """ Check for files on the file system """
        if os.path.exists(csvfile):
            if os.path.isdir(csvfile):
                self.csvfile = []
                for afile in os.listdir(csvfile):
                    if afile.endswith('.csv'):
                        filepath = os.path.join(csvfile, afile)
                        try:
                            lines = self.__csvfile(filepath)
                            self.csvfile.extend(lines)
                        except:
                            pass
            else:
                self.csvfile = self.__csvfile(csvfile)
        if not getattr(self, 'csvfile', []):
            raise Exception('File %s not found' % csvfile)

class Command(LabelCommand, CSVParser):
    """
    Inspect a CSV resource to generate the code for a Django model.
    """

    option_list = BaseCommand.option_list + (
               make_option('--defaults', default='',
                           help='''Provide comma separated defaults for the import 
                                   (field1=value,field3=value, ...)'''),
               make_option('--model', default='',
                           help='Please provide the model to import to'),
               make_option('--charset', default='',
                           help='Force the charset conversion used rather than detect it')
                   )
    help = "Analyses CSV file date to generate a Django model"

    def __init__(self):
        """ Set default attributes data types """
        super(Command, self).__init__()
        self.csvfile = []
        self.charset = ''
        self.filehandle = None
        self.makemodel = ''

    def handle_label(self, label, **options):
        """ Handle the circular reference by passing the nested
            save_csvimport function
        """
        csvfile = label
        defaults = options.get('defaults', [])
        model = options.get('model', '')
        if not model:
            model = label.split('.')[0]
        charset = options.get('charset', '')

        self.defaults = self.set_mappings(defaults)
        self.check_filesystem(csvfile)
        app_label = 'csvimport'
        self.makemodel = '""" A django model generated with django-csvimport csvinspect\n'
        self.makemodel += '    which used OKN messytables to guess data types - may need some manual tweaks!\n"""'
        self.makemodel += '\nfrom django.db import models\n\n'
        self.makemodel += self.create_new_model(model)
        print self.makemodel
        return

    def create_new_model(self, modelname):
        """ Use messytables to guess field types and build a new model """

        nocols = False
        cols = self.csvfile[0]
        for col in cols:
            if not col:
                nocols = True
        if nocols:
            cols = ['col_%s' % num for num in range(1, len(cols))]
            print 'No column names for %s columns' % len(cols)
        else:
            cols = [cleancol.sub('_', col).lower() for col in cols]
        try:
            from messytables import any_tableset, type_guess
        except:
            self.errors.append('If you want to inspect CSV files to generate model code, you must install https://messytables.readthedocs.org')
            self.modelname = ''
            return
        try:
            table_set = any_tableset(self.filehandle)
            row_set = table_set.tables[0]
            types = type_guess(row_set.sample)
            types = [str(typeobj) for typeobj in types]
        except:
            self.errors.append('messytables could not guess your column types')
            self.modelname = ''
            return

        fieldset = []
        maximums = self.get_maxlengths(cols)
        for i, col in enumerate(cols):
            length = maximums[i]
            if types[i] == 'String' and length>255:
                types[i] = 'Text'
            integer = length
            decimal = int(length/2)
            if decimal > 10:
                decimal = 10
            blank = True
            default = True
            column = (col, types[i], length, length, integer, decimal, blank, default)
            fieldset.append(column)
        from ...make_model import MakeModel
        maker = MakeModel()
        return maker.model_from_table(modelname, fieldset)

    def get_maxlengths(self, cols):
        """ Get maximum column length values to avoid truncation 
            -- can always manually reduce size of fields after auto model creation
        """
        maximums = [0]*len(cols)
        for line in self.csvfile[1:100]:
            for i, value in enumerate(line):
                if value and len(value) > maximums[i]:
                    maximums[i] = len(value)
                if maximums[i] > 10:
                    maximums[i] += 10
                if not maximums[i]:
                    maximums[i] = 10
        return maximums

