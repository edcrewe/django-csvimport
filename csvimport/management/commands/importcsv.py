""" Developed for www.heliosfoundation.org by Ed Crewe and Tom Dunham
    Django command to import CSV files
"""
import os
import csv
import re
from datetime import datetime

import codecs
import chardet
import django
from distutils.version import StrictVersion

from django.db import DatabaseError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import LabelCommand, BaseCommand, CommandError
from optparse import make_option
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

CURRENT_TIMEZONE = timezone.get_current_timezone()
try:
    from django.db.models.loading import get_model
except ImportError:
    from django.apps import apps

    get_model = apps.get_model

from django.conf import settings
from csvimport.parser import CSVParser
from csvimport.signals import imported_csv, importing_csv

CSVIMPORT_LOG = getattr(settings, "CSVIMPORT_LOG", "screen")
if CSVIMPORT_LOG == "logger":
    import logging

    logger = logging.getLogger(__name__)

INTEGER = [
    "BigIntegerField",
    "IntegerField",
    "SmallIntegerField",
    "AutoField",
    "PositiveIntegerField",
    "PositiveSmallIntegerField",
]
FLOAT = ["DecimalField", "FloatField"]
NUMERIC = INTEGER + FLOAT
SMALLINT_DBS = ["sqlite", "sqlite3", "sqlite4"]
DATE = ["DateField", "TimeField", "DateTimeField"]
BOOLEAN = ["BooleanField", "NullBooleanField"]
BOOLEAN_TRUE = [1, "1", "Y", "Yes", "yes", "True", "true", "T", "t"]

# Adding Support for Django 1.9+
if StrictVersion(django.get_version()) >= StrictVersion("1.9.0"):
    DATE_INPUT_FORMATS = tuple(settings.DATE_INPUT_FORMATS) or ("%d/%m/%Y", "%Y/%m/%d")
else:
    DATE_INPUT_FORMATS = settings.DATE_INPUT_FORMATS or ("%d/%m/%Y", "%Y/%m/%d")

CSV_DATE_INPUT_FORMATS = DATE_INPUT_FORMATS + ("%d-%m-%Y", "%Y-%m-%d")
cleancol = re.compile("[^0-9a-zA-Z]+")  # cleancol.sub('_', s)

from django import dispatch

imported_csv = dispatch.Signal(providing_args=["instance", "row"])
importing_csv = dispatch.Signal(providing_args=["instance", "row"])


# Note if mappings are manually specified they are of the following form ...
# MAPPINGS = "column1=shared_code,column2=org(Organisation|name),column3=description"
# statements = re.compile(r";[ \t]*$", re.M)


def save_csvimport(props=None, instance=None):
    """ To avoid circular imports do saves here """
    try:
        if not instance:
            from csvimport.models import CSVImport

            csvimp = CSVImport()
        if props:
            for key, value in props.items():
                setattr(csvimp, key, value)
        csvimp.save()
        return csvimp.id
    except:
        # Running as command line
        if instance.charset:
            print("Assumed charset = %s\n" % instance.charset)
        print("\n------------ %s ------------" % instance.model.__name__)
        string_types = (type(u""), type(""))
        for line in instance.loglist:
            if type(line) not in string_types:
                for subline in line:
                    print(subline)
            else:
                print(line)
        return


class Command(LabelCommand, CSVParser):
    """
    Parse and import a CSV resource to a Django model.

    Notice that the doc tests are merely illustrational, and will not run
    as is.
    """

    options = {
        "mappings": {
            "default": False,
            "help": """Provide comma separated column names or format like
                                           (column1=field1(ForeignKey|field),column2=field2(ForeignKey|field), ...)
                                           for the import (use none for no names -> col_#)""",
        },
        "defaults": {
            "default": False,
            "help": """Provide comma separated defaults for the import
                                           (field1=value,field3=value, ...)""",
        },
        "model": {
            "default": "csvimport.Country",
            "help": "Please provide the model to import to",
        },
        "charset": {
            "default": False,
            "help": "Force the charset conversion used rather than detect it",
        },
        "delimiter": {
            "default": ",",
            "help": "Specify the CSV delimiter - default is comma, use \t for tab",
        },
        "clean": {
            "default": True,
            "help": "If its invalid, change numeric and date data to valid min/max values",
        },
        "bulk": {
            "default": False,
            "help": "If True, all csv rows are created at once by a bulk create, so can fail if any have data issues, but its faster",
        },
    }

    # Use 1.10 or later arguments method
    def add_arguments(self, parser):
        parser.add_argument(
            "csvfile",
            help="The file system path to the CSV file with the data to import",
        )
        for arg in self.options:
            parser.add_argument("--%s" % arg, **self.options[arg])

    # Support for Django 1.9 or earlier
    if StrictVersion(django.get_version()) < StrictVersion("1.10.0"):
        make_options = []
        for arg in options:
            make_options.append(make_option("--%s" % arg, **options[arg]))
        option_list = BaseCommand.option_list + tuple(make_options)

    help = "Imports a CSV file to a model"

    def __init__(self):
        """ Set default attributes data types """
        super(Command, self).__init__()
        self.props = {}
        self.debug = False
        self.errors = []
        self.loglist = []
        self.mappings = []
        self.defaults = []
        self.app_label = ""
        self.model = ""
        self.fieldmap = {}
        self.file_name = ""
        self.nameindexes = False
        self.deduplicate = True
        self.csvfile = []
        self.charset = ""
        self.filehandle = None
        self.makemodel = ""
        self.start = 1
        self.db_backend = ""

    def handle(self, *args, **options):
        if args:
            label = args[0]
        else:
            label = options.get("csvfile")
        self.handle_label(label, **options)

    def handle_label(self, label, **options):
        """ Handle the circular reference by passing the nested
            save_csvimport function
        """
        self.loglist = []
        filename = label
        mappings = options.get("mappings", [])
        defaults = options.get("defaults", [])
        modelname = options.get("model", "Item")
        charset = options.get("charset", "")
        delimiter = options.get("delimiter", ",")
        clean = options.get("clean", True)
        bulk = options.get("bulk", False)
        # show_traceback = options.get('traceback', True)
        warn = self.setup(
            mappings=mappings,
            modelname=modelname,
            charset=charset,
            csvfile=filename,
            defaults=defaults,
            delimiter=delimiter,
            clean=clean,
            bulk=bulk,
        )
        if not warn and not hasattr(self.model, "_meta"):
            warn = (
                "Sorry your model could not be found please check app_label.modelname = %s"
                % modelname
            )
        if warn:
            try:
                print(warn)
            except:
                self.loglist.append(warn)
                raise CommandError(warn)
            return
        self.loglist.extend(self.run())
        if self.props:
            save_csvimport(self.props, self)
        return

    def setup(
        self,
        mappings,
        modelname,
        charset,
        csvfile="",
        defaults="",
        uploaded=None,
        nameindexes=False,
        deduplicate=True,
        delimiter=",",
        reader=True,
        clean=True,
        bulk=False,
    ):
        """ Setup up the attributes for running the import """
        self.clean = clean
        self.bulk = bulk
        self.defaults = self.set_mappings(defaults)
        if modelname.find(".") > -1:
            app_label, model = modelname.split(".")
        if uploaded:
            self.csvfile = self.open_csvfile(
                uploaded.path, delimiter=delimiter, reader=reader
            )
        else:
            failed = self.check_filesystem(csvfile, delimiter=delimiter, reader=reader)
            if failed:
                return failed
        self.charset = charset
        self.app_label = app_label
        self.model = get_model(app_label, model)
        if not self.model:
            return "No model found for %s.%s" % (app_label, model)
        try:
            db_name = self.model()._state.db or "default"
            self.db_backend = settings.DATABASES[db_name]["ENGINE"].split(".")[-1]
        except:
            pass
        for field in self.model._meta.fields:
            self.fieldmap[field.name] = field
            if field.__class__ == models.ForeignKey:
                self.fieldmap[field.name + "_id"] = field
        if mappings:
            if mappings == "none":
                # Use auto numbered cols instead - eg. from create_new_model
                mappings = self.parse_header(
                    ["col_%s" % num for num in range(1, len(self.csvfile[0]))]
                )
            # Test for column=name or just name list format
            if mappings.find("=") == -1:
                mappings = self.parse_header(mappings.split(","))
            self.mappings = self.set_mappings(mappings)
        self.nameindexes = bool(nameindexes)
        self.file_name = csvfile
        self.deduplicate = deduplicate
        return

    def make_row(self, row, csvimportid, index, loglist, clean=True):
        """Create an instance of the model and populate it with the rows data"""
        model_instance = self.model()
        model_instance.csvimport_id = csvimportid

        for (column, field, foreignkey) in self.mappings:
            if self.nameindexes:
                column = indexes.index(column)
            else:
                column = int(column) - 1

            if foreignkey:
                if len(row) <= column:
                    msg = (
                        "row %s: FKey %s couldnt be set for row - because the row is not parsable - skipping it"
                        % (index, field)
                    )
                    loglist.append(msg)
                    return None
                else:
                    row[column] = self.insert_fkey(foreignkey, row[column])

            if self.debug:
                loglist.append(
                    '%s.%s = "%s"' % (self.model.__name__, field, row[column])
                )
            try:
                if clean:
                    row[column] = self.type_clean(field, row[column], loglist, index)
            except:
                pass
            try:
                model_instance.__setattr__(field, row[column])
            except:
                try:
                    field = getattr(model_instance, field)
                    if field:
                        value = field.to_python(row[column])
                except:
                    if not msg:
                        msg = "row %s: Column %s = %s couldnt be set for row" % (
                            index,
                            field,
                            row[column],
                        )
                        loglist.append(msg)

        return model_instance

    def run(self, logid=0):
        """ Run the csvimport """
        loglist = []
        if self.nameindexes:
            indexes = self.csvfile.pop(0)
        counter = 0
        if logid:
            csvimportid = logid
        else:
            csvimportid = 0

        if self.mappings:
            self.start = 0
            loglist.append("Manually entered mapping list")
        else:
            mappingstr = self.parse_header(self.csvfile[0])
            if mappingstr:
                loglist.append("Mapping from first, header, row of CSV file")
                self.mappings = self.set_mappings(mappingstr)
        if not self.mappings:
            if not self.model:
                loglist.append("Outputting setup message")
            else:
                warn = (
                    "No fields in the CSV file match "
                    + self.model._meta.app_label
                    + "."
                    + self.model.__name__
                )
                warn += " - you must add a header field name row to the CSV file or supply a mapping list"
                loglist.append(warn)
            return loglist

        # count before import
        rowcount = self.model.objects.count()
        models = []
        for i, row in enumerate(self.csvfile[self.start :]):
            if CSVIMPORT_LOG == "logger":
                logger.info("Import %s %i", self.model.__name__, counter)
            counter += 1
            model_instance = self.make_row(row, csvimportid, i, loglist, self.clean)
            if self.bulk:
                models.append(model_instance)
            else:
                with transaction.atomic():
                    try:
                        self.row_insert(row, model_instance, loglist)
                    except:
                        pass
            # loglist = []
        if models and self.bulk:
            models[0].__class__.objects.bulk_create(models)
        # count after import
        rowcount = self.model.objects.count() - rowcount
        countmsg = "Imported %s rows to %s" % (rowcount, self.model.__name__)
        if CSVIMPORT_LOG == "logger":
            logger.info(countmsg)
        if loglist:
            loglist.append(countmsg)
            self.props = {
                "file_name": self.file_name,
                "import_user": "cron",
                "upload_method": "cronjob",
                "error_log": "\n".join(loglist),
                "import_date": datetime.now(),
            }
            return loglist
        else:
            return ["No logging"]

    def row_insert(self, row, model_instance, loglist):
        """ Insert a row - separate function for transaction wrapping """
        msg = ""
        if model_instance:
            if self.defaults:
                for (field, value, foreignkey) in self.defaults:
                    value = self.type_clean(field, value, loglist)
                    try:
                        done = model_instance.getattr(field)
                    except:
                        done = False
                    if not done:
                        if foreignkey:
                            value = self.insert_fkey(foreignkey, value)
                    if value:
                        model_instance.__setattr__(field, value)

            if self.deduplicate:
                matchdict = {}
                for (column, field, foreignkey) in self.mappings:
                    matchdict[field + "__exact"] = getattr(model_instance, field, None)
                try:
                    self.model.objects.get(**matchdict)
                    return
                except:
                    pass
            try:
                importing_csv.send(
                    sender=model_instance, row=dict(zip(self.csvfile[:1][0], row))
                )
                model_instance.save()
                imported_csv.send(
                    sender=model_instance, row=dict(zip(self.csvfile[:1][0], row))
                )
            except DatabaseError as err:
                try:
                    error_number, error_message = err
                except:
                    error_message = err
                    error_number = 0
                # Catch duplicate key error.
                if error_number != 1062:
                    loglist.append(
                        "Database Error: %s, Number: %d" % (error_message, error_number)
                    )
            except ValueError as err:
                # Usually only occurs if clean=False
                loglist.append(str(err))
            # except OverflowError:
            #    pass
            if CSVIMPORT_LOG == "logger":
                for line in loglist:
                    logger.info(line)

    def type_clean(self, field, value, loglist, row=0):
        """ Data value clean up - type formatting"""
        if not self.fieldmap.get(field):
            raise Exception(
                "Fieldmap is not populated for %s -\n%s" % (field, self.fieldmap)
            )
        field_type = self.fieldmap.get(field).get_internal_type()

        try:
            value = value.strip()
        except AttributeError:
            pass

        # Tidy up boolean data
        if field_type in BOOLEAN:
            value = value in BOOLEAN_TRUE
            # sqlite fix since it just uses int under the hood
            if self.db_backend in SMALLINT_DBS:
                if value:
                    value = 1
                else:
                    value = 0

        # Tidy up numeric data
        if field_type in NUMERIC:
            if not value:
                value = 0
            else:
                try:
                    value = float(value)
                except:
                    loglist.append(
                        "row %s: Column %s = %s is not a number so is set to 0"
                        % (row, field, value)
                    )
                    value = 0
            if field_type in INTEGER:
                # 1e+28 = 9999999999999999583119736832L
                if value > 9223372036854775807:
                    intmsg = (
                        "row %s: Column %s = %s more than the max integer 9223372036854775807"
                        % (row, field, value)
                    )
                    if self.db_backend in SMALLINT_DBS:
                        intmsg += " sqlite may error with big integers so rounded down"
                        value = 9223372036854775807
                    loglist.append(intmsg)
                if str(value).lower() in ("nan", "inf", "+inf", "-inf"):
                    loglist.append(
                        "row %s: Column %s = %s is not an integer so is set to 0"
                        % (row, field, value)
                    )
                    value = 0
                value = int(value)
                if value < 0 and field_type.startswith("Positive"):
                    loglist.append(
                        "row %s: Column %s = %s, less than zero so set to 0"
                        % (row, field, value)
                    )
                    value = 0
        # date data - remove the date if it doesn't convert so null=True can work
        if field_type in DATE:
            datevalue = None
            try:
                datevalue = datetime(value)
            except:
                for datefmt in CSV_DATE_INPUT_FORMATS:
                    try:
                        datevalue = datetime.strptime(value, datefmt)
                    except:
                        pass

            if datevalue:
                value = timezone.make_aware(datevalue, CURRENT_TIMEZONE)
            else:
                # loglist.append('row %s: Column %s = %s not date format' % (i, field, value))
                value = None
        return value

    def parse_header(self, headlist):
        """ Parse the list of headings and match with self.fieldmap """
        mapping = []
        found = []
        headlist = [cleancol.sub("_", col) for col in headlist]
        logstr = ""
        for i, heading in enumerate(headlist):
            for key in (
                (heading, heading.lower()) if heading != heading.lower() else (heading,)
            ):
                if key in self.fieldmap:
                    found.append(key.lower())
                    field = self.fieldmap[key]
                    key = self.check_fkey(key, field)
                    mapping.append("column%s=%s" % (i + 1, key))
        for key in headlist:
            if key.lower() not in found:
                logstr += ", %s" % key
        if mapping:
            mappingstr = ",".join(mapping)
            if logstr:
                logmsg = "CSV header unmatched ignored cols = %s" % logstr[2:]
            else:
                logmsg = "CSV header matched all cols"
            self.loglist.append(logmsg)
            return mappingstr
        return ""

    def insert_fkey(self, foreignkey, rowcol):
        """ Add fkey if not present
            If there is corresponding data in the model already,
            we do not need to add more, since we are dealing with
            foreign keys, therefore foreign data
        """
        fk_key, fk_field = foreignkey
        if fk_key and fk_field:
            # Allow users to specify app label for fk model if they want
            if fk_key.find(".") > -1:
                new_app_label, fk_key = fk_key.split(".")
            else:
                try:
                    new_app_label = ContentType.objects.get(model=fk_key).app_label
                except:
                    new_app_label = self.app_label
            fk_model = get_model(new_app_label, fk_key)
            matches = fk_model.objects.filter(**{fk_field + "__exact": rowcol})

            if not matches:
                key = fk_model()
                key.__setattr__(fk_field, rowcol)
                key.save()

            rowcol = fk_model.objects.filter(**{fk_field + "__exact": rowcol})[0]
        return rowcol

    def check_fkey(self, key, field):
        """ Build fkey mapping via introspection of models """
        # TODO fix to find related field name rather than assume second field
        if not key.endswith("_id"):
            if field.__class__ == models.ForeignKey:
                try:
                    parent = field.remote_field.model
                except AttributeError:
                    try:
                        parent = field.related.parent_model
                    except AttributeError:
                        parent = field.related.model
                key += "(%s|%s)" % (parent.__name__, parent._meta.fields[1].name)
        return key

    def error(self, message, type=1):
        """
        Types:
            0. A fatal error. The most drastic one. Will quit the program.
            1. A notice. Some minor thing is in disorder.
        """

        types = (("Fatal error", FatalError), ("Notice", None))

        self.errors.append((message, type))

        if type == 0:
            # There is nothing to do. We have to quit at this point
            raise Exception(types[0][1], message)
        elif self.debug:
            print("%s: %s" % (types[type][0], message))


class FatalError(Exception):
    """
    Something really bad happened.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
