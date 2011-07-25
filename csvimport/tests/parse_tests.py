import os

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from csvimport.management.commands.csvimport import Command
from csvimport.tests.models import Item

class DummyFileObj:
    path = ''

    def set_path(self, filename):
        self.path = os.path.join(os.path.dirname(__file__), 
                                 'fixtures',
                                 filename)

class CommandParseTest(TestCase):
    """ Run test of file parsing """

    def test_parse(self, filename='test.csv'):
        """ Use custom command to upload file and parse it into Items """
        cmd = Command()
        uploaded = DummyFileObj()
        uploaded.set_path(filename)
        cmd.setup(mappings='', 
                  modelname='tests.Item', 
                  uploaded=uploaded,
                  defaults='country=KE(Country|code)')

        # Report back any parse errors and fail test if they exist
        errors = cmd.run(logid='commandtest')
        if errors:
            for err in errors:
                print err
        self.assertEqual(errors, None)

        try:
            item = Item.objects.get(code_share__exact='sheeting')
        except ObjectDoesNotExist:
            print 'Failed to get row from imported test.csv Items'

        # Check a couple of the fields in Item    
        self.assertEqual(item.code_org, 'RF007')
        self.assertEqual(item.description, 'Plastic sheeting, 4*60m, roll')
        # Check related Organisation model is created
        self.assertEqual(item.organisation.name, 'Save UK')
