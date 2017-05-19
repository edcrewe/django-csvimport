""" Core CSV parser class that is used by the management commands """
import os
import re
import csv
import sys
import codecs
import re
pyversion = sys.version_info[0]  # python 2 or 3


class CSVParser(object):
    """ Open a CSV file, check its encoding and parse it into memory
        and set up the map of the fields
    """

    csvfile = []
    charset = ''
    filehandle = None
    check_cols = False
    string_types = (type(u''), type(''))

    def list_rows(self, rows):
        """ CSV Reader returns an iterable, but as we possibly need to
            perform list commands and since list is an acceptable iterable,
            we'll just transform it.
            Also do optional column count consistency check here
        """
        if rows and self.check_cols:
            rowlen = 0
            for row in rows:
                if not rowlen:
                    rowlen = len(row)
                else:
                    if rowlen != len(row):
                        self.error('''Sorry you have inconsistent numbers of cols in your CSV rows
                                      But you have requested column count checking - so no data has been imported
                                   ''')
                        return []
        return list(rows)

    def open_csvfile(self, datafile, delimiter=',', reader=True):
        """ Detect file encoding and open appropriately """
        self.filehandle = open(datafile, 'rb')
        if not self.charset:
            import chardet
            diagnose = chardet.detect(self.filehandle.read())
            self.charset = diagnose['encoding']
        rows = []
        if reader:
            try:
                csvfile = codecs.open(datafile, 'r', self.charset)
            except IOError:
                self.error('Could not open specified csv file, %s, or it does not exist' % datafile, 0)
            else:
                try:
                    csvgenerator = self.charset_csv_reader(csv_data=csvfile, charset=self.charset, delimiter=delimiter)
                    rows = [row for row in csvgenerator]
                    return self.list_rows(rows)
                except:
                    pass
        # Sometimes encoding is too mashed to be able to open the file as text with csv_reader
        # ... especially in Python 3 - its a lot stricter
        # so reopen as raw unencoded and just try and get lines out one by one
        output = []
        count = 0
        expression = r"""(['"]*)(.*?)\1(""" + delimiter + r"""|$)"""
        csvsplit = re.compile(expression)
        if not rows:
            content = None
            try:
                with open(datafile, 'rb') as content_file:
                    content = content_file.readlines()
            except:
                self.loglist.append('Failed to open file %s' % datafile)
            if type(content) not in self.string_types and len(content) == 1:
                content = content[0]
            content_type = type(content)

            if content_type in self.string_types:
                endings = ('\r\n', '\r', '\\r', '\n')
            elif isinstance(b'', content_type):  # string in python2 / bytes in python3
                endings = (b'\r\n', b'\r', b'\\r', b'\n')
            else:
                endings = None

            if endings:
                for ending in endings:
                    if content.find(ending) > -1:
                        rows = content.split(ending)
                        break
            if not rows:
                rows = content

        if rows:
            for row in rows:
                if pyversion == 3:
                    row = row.decode(self.charset)
                if type(row) in self.string_types:
                    # FIXME: Works for test fixtures - but rather hacky csvreader replacement regex splitter
                    # breaks unless empty cols have a space added!
                    row = row.replace(',,', ', ,')
                    row = row.replace('""', '" "')
                    row = row.replace("''", "' '")
                    row = csvsplit.split(row)
                    row = [item for item in row if item and item not in (delimiter, '"', "'")]
                    if pyversion == 2:
                        try:
                            row = [unicode(item, self.charset) for item in row]
                        except:
                            row = []
                if row:
                    count += 1
                    try:
                        output.append(row)
                    except:
                        self.loglist.append('Failed to parse row %s' % count)
        return self.list_rows(output)

    def charset_csv_reader(self, csv_data, dialect=csv.excel,
                           charset='utf-8', delimiter=',', **kwargs):
        csv_reader = csv.reader(self.charset_encoder(csv_data, charset),
                                dialect=dialect, delimiter=delimiter, **kwargs)
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
                mappings[mapp] = list(mappings[mapp])  # [unicode(item) for item in list(mappings[mapp])]
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

            if found is not None:
                return (found.group(1), found.group(2))
            else:
                return None

        mappings = mappings.replace(',', ' ')
        mappings = mappings.replace('column', '')
        return parse_mapping(mappings)

    def check_filesystem(self, csvfile):
        """ Check for files on the file system """
        if csvfile and os.path.exists(csvfile):
            if os.path.isdir(csvfile):
                self.csvfile = []
                for afile in os.listdir(csvfile):
                    if afile.endswith('.csv'):
                        filepath = os.path.join(csvfile, afile)
                        try:
                            lines = self.open_csvfile(filepath)
                            self.csvfile.extend(lines)
                        except:
                            pass
            else:
                self.csvfile = self.open_csvfile(csvfile)
        if not getattr(self, 'csvfile', []):
            return 'File "%s" not found' % csvfile
        return ''
