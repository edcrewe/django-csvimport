import os

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from csvimport.management.commands.csvimport import Command
from csvimport.tests.models import Item

class DummyFileObj:
    """ Use to replace html upload / or command arg 
        with test fixtures files 
    """
    path = ''

    def set_path(self, filename):
        self.path = os.path.join(os.path.dirname(__file__), 
                                 'fixtures',
                                 filename)

class CommandParseTest(TestCase):
    """ Run test of file parsing """

    def command(self, filename, defaults='country=KE(Country|code)'):
        """ Run core csvimport command to parse file """
        cmd = Command()
        uploaded = DummyFileObj()
        uploaded.set_path(filename)
        cmd.setup(mappings='', 
                  modelname='tests.Item', 
                  uploaded=uploaded,
                  defaults=defaults)

        # Report back any parse errors and fail test if they exist
        errors = cmd.run(logid='commandtest')
        if errors:
            for err in errors:
                print err
        self.assertEqual(errors, None)

    def get_item(self, code_share='sheeting'):
        """ Get item for confirming import is OK """
        try:
            item = Item.objects.get(code_share__exact=code_share)
        except ObjectDoesNotExist:
            item = None
        self.assertTrue(item, 'Failed to get row from imported test.csv Items')
        return item

    def test_plain(self, filename='test_plain.csv'):
        """ Use custom command to upload file and parse it into Items """
        self.command(filename)
        item = self.get_item('sheeting')
        # Check a couple of the fields in Item    
        self.assertEqual(item.code_org, 'RF007')
        self.assertEqual(item.description, 'Plastic sheeting, 4*60m, roll')
        # Check related Organisation model is created
        self.assertEqual(item.organisation.name, 'Save UK')
        Item.objects.all().delete()

    def test_char(self, filename='test_char.csv'):
        """ Use custom command to upload file and parse it into Items """
        self.command(filename)
        item = self.get_item('watercan')
        self.assertEqual(item.code_org, 'CWATCONT20F')
        self.assertEqual(item.quantity, 1000)
        #FIXME: self.assertEqual(unicode(item.uom), u'pi\u7e26e')
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()
