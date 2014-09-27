""" Core CSV parser class that is used by the management commands """
import os, re
import csv
import codecs

class CSVParser(object):
    """ Open a CSV file, check its encoding and parse it into memory 
        and set up the map of the fields
    """

    csvfile = []
    charset = ''
    filehandle = None

    def open_csvfile(self, datafile):
        """ Detect file encoding and open appropriately """
        self.filehandle = open(datafile)
        if not self.charset:
            import chardet
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
                mappings[mapp] = list(mappings[mapp]) #[unicode(item) for item in list(mappings[mapp])]
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
                            lines = self.open_csvfile(filepath)
                            self.csvfile.extend(lines)
                        except:
                            pass
            else:
                self.csvfile = self.open_csvfile(csvfile)
        if not getattr(self, 'csvfile', []):
            return 'File %s not found' % csvfile
        return ''
