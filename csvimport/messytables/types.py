import decimal
import datetime
from collections import defaultdict
import locale
import sys

from csvimport.messytables.dateparser import DATE_FORMATS, is_date


class CellType(object):
    """A cell type maintains information about the format
    of the cell, providing methods to check if a type is
    applicable to a given value and to convert a value to the
    type."""

    guessing_weight = 1
    # the type that the result will have
    result_type = None

    def test(self, value):
        """Test if the value is of the given type. The
        default implementation calls ``cast`` and checks if
        that throws an exception. True or False"""
        if isinstance(value, self.result_type):
            return True
        try:
            self.cast(value)
            return True
        except Exception:
            return False

    @classmethod
    def instances(cls):
        return [cls()]

    def cast(self, value):
        """Convert the value to the type. This may throw
        a quasi-random exception if conversion fails."""
        return value

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash(self.__class__)

    def __repr__(self):
        return self.__class__.__name__.rsplit("Type", 1)[0]


class StringType(CellType):
    """A string or other unconverted type."""

    result_type = str

    def cast(self, value):
        if value is None:
            return None
        if isinstance(value, self.result_type):
            return value
        try:
            return str(value)
        except UnicodeEncodeError:
            return str(value)


class IntegerType(CellType):
    """An integer field."""

    guessing_weight = 6
    result_type = int

    def cast(self, value):
        if value in ("", None):
            return None

        try:
            value = float(value)
        except Exception:
            # get rid of thousands separators
            # e.g. "1,000"
            return locale.atoi(value)

        if value.is_integer():
            return int(value)
        else:
            raise ValueError("Invalid integer: %s" % value)


class DecimalType(CellType):
    """Decimal number, ``decimal.Decimal`` or float numbers."""

    guessing_weight = 4
    result_type = decimal.Decimal

    def cast(self, value):
        if value in ("", None):
            return None
        try:
            return decimal.Decimal(value)
        except Exception:
            # get rid of thousands separators
            # e.g. "1,000.00"
            value = locale.atof(value)
            if sys.version_info < (2, 7):
                value = str(value)
            return decimal.Decimal(value)


class PercentageType(DecimalType):
    """Decimal number, ``decimal.Decimal`` or float numbers."""

    guessing_weight = 0

    def cast(self, value):
        result = DecimalType.cast(self, value)
        if result:
            result = result / decimal.Decimal("100")
        return result


class CurrencyType(DecimalType):
    guessing_weight = 0
    result_type = decimal.Decimal

    def cast(self, value):
        value_without_currency = value.split(" ")[0]
        return DecimalType.cast(self, value_without_currency)


class FloatType(DecimalType):
    """FloatType is deprecated"""

    pass


class BoolType(CellType):
    """A boolean field. Matches true/false, yes/no and 0/1 by default,
    but a custom set of values can be optionally provided.
    """

    guessing_weight = 7
    result_type = bool
    true_values = ("yes", "true", "0")
    false_values = ("no", "false", "1")

    def __init__(self, true_values=None, false_values=None):
        if true_values is not None:
            self.true_values = true_values
        if false_values is not None:
            self.false_values = false_values

    def cast(self, value):
        s = value.strip().lower()
        if value in ("", None):
            return None
        if s in self.true_values:
            return True
        if s in self.false_values:
            return False
        raise ValueError


class TimeType(CellType):
    result_type = datetime.time

    def cast(self, value):
        if isinstance(value, self.result_type):
            return value
        if value in ("", None):
            return None
        hour = int(value[2:4])
        minute = int(value[5:7])
        second = int(value[8:10])
        if hour < 24:
            return datetime.time(hour, minute, second)
        else:
            return datetime.timedelta(hours=hour, minutes=minute, seconds=second)


class DateType(CellType):
    """The date type is special in that it also includes a specific
    date format that is used to parse the date, additionally to the
    basic type information."""

    guessing_weight = 3
    formats = DATE_FORMATS
    result_type = datetime.datetime

    def __init__(self, format):
        self.format = format

    @classmethod
    def instances(cls):
        return [cls(v) for v in cls.formats]

    def test(self, value):
        if isinstance(value, str) and not is_date(value):
            return False
        return CellType.test(self, value)

    def cast(self, value):
        if isinstance(value, self.result_type):
            return value
        if value in ("", None):
            return None
        if self.format is None:
            return value
        return datetime.datetime.strptime(value, self.format)

    def __eq__(self, other):
        return isinstance(other, DateType) and self.format == other.format

    def __repr__(self):
        return "Date(%s)" % self.format

    def __hash__(self):
        return hash(self.__class__) + hash(self.format)


TYPES = [
    StringType,
    DecimalType,
    IntegerType,
    DateType,
    BoolType,
    TimeType,
    CurrencyType,
    PercentageType,
]


def type_guess(rows, types=TYPES):
    """The type guesser aggregates the number of successful
    conversions of each column to each type, weights them by a
    fixed type priority and select the most probable type for
    each column based on that figure. It returns a list of
    ``CellType``. Empty cells are ignored.

    Modified original messytables.type_quess
    to use simple rows = list of lists of cell values
    ie inspectcsv self.csvfile with cols first row removed if exists

    All columns are checked for all types so this can be slow for huge CSV files
    so make a sample file with a subset of the data for this use case.
    """
    guesses = []
    type_instances = [i for t in types for i in t.instances()]
    for i, row in enumerate(rows):
        diff = len(row) - len(guesses)
        for _ in range(diff):
            guesses.append(defaultdict(int))
        for i, cell in enumerate(row):
            # add string guess so that we have at least one guess
            guesses[i][StringType()] = guesses[i].get(StringType(), 0)
            if not cell:
                continue
            for type in type_instances:
                if type.test(cell):
                    guesses[i][type] += type.guessing_weight
    _columns = []
    for guess in guesses:
        # this first creates an array of tuples because we want the types to be
        # sorted. Even though it is not specified, python chooses the first
        # element in case of a tie
        # See: http://stackoverflow.com/a/6783101/214950
        guesses_tuples = [(t, guess[t]) for t in type_instances if t in guess]
        _columns.append(max(guesses_tuples, key=lambda t_n: t_n[1])[0])
    return _columns
