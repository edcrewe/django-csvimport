""" Base test case for command line manage.py csvimport """
import os

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from csvimport.management.commands.csvimport import Command
from csvimport.tests.models import Item

DEFAULT_ERRS = ['Using mapping from first row of CSV file', ]


class DummyFileObj():
    """ Use to replace html upload / or command arg
        with test fixtures files
    """
    path = ''

    def set_path(self, filename):
        self.path = os.path.join(os.path.dirname(__file__),
                                 'fixtures',
                                 filename)

class CommandTestCase(TestCase):
    """ Run test of use of optional command line args - mappings, default and charset """

    def command(self, filename, 
                defaults='country=KE(Country|code)',
                mappings='',
                expected_errs=[]):
        """ Run core csvimport command to parse file """
        cmd = Command()
        uploaded = DummyFileObj()
        uploaded.set_path(filename)
        cmd.setup(mappings=mappings,
                  modelname='tests.Item',
                  charset='',
                  uploaded=uploaded,
                  defaults=defaults)

        # Report back any unnexpected parse errors
        # and confirm those that are expected.
        # Fail test if they are not matching
        errors = cmd.run(logid='commandtest')
        expected = [err for err in DEFAULT_ERRS]
        if expected_errs:
            expected.extend(expected_errs)
            expected.reverse()
        for err in expected:
            try:
                error = errors.pop()
                self.assertEqual(error, err)
            except:
                pass
        if errors:
            for err in errors:
                print err
        self.assertEqual(errors, [])

    def get_item(self, code_share='sheeting'):
        """ Get item for confirming import is OK """
        try:
            item = Item.objects.get(code_share__exact=code_share)
        except ObjectDoesNotExist:
            item = None
        self.assertTrue(item, 'Failed to get row from imported test.csv Items')
        return item
