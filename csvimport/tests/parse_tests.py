# -*- coding: utf-8 -*-
# Use unicode source code to make test character string writing easier
import os

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from csvimport.management.commands.csvimport import Command
from csvimport.tests.models import Country, UnitOfMeasure, Item, Organisation

DEFAULT_ERRS = ['Using mapping from first row of CSV file', ]

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

    def command(self, filename, defaults='country=KE(Country|code)',
                expected_errs=[]):
        """ Run core csvimport command to parse file """
        cmd = Command()
        uploaded = DummyFileObj()
        uploaded.set_path(filename)
        cmd.setup(mappings='', 
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
            error = errors.pop()
            self.assertEqual(error, err)
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
        """ Use custom command parse file - test with odd non-ascii character """
        self.command(filename)
        item = self.get_item('watercan')
        self.assertEqual(item.code_org, 'CWATCONT20F')
        self.assertEqual(item.quantity, 1000)
        # self.assertEqual(unicode(item.uom), u'pi縦e')
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()

    def test_char2(self, filename='test_char2.csv'):
        """ Use custom command to parse file with range of unicode characters """
        self.command(filename)
        item = self.get_item(u"Cet élément est utilisé par quelqu'un d'autre et ne peux être modifié")
        self.assertEqual(item.description, 
                         "TENTE FAMILIALE, 12 m_, COMPLETE (tapis de sol/double toit)")
        self.assertEqual(item.quantity, 101)
        self.assertEqual(unicode(item.uom), u'删除当前图片')
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()

    def test_duplicate(self, filename='test_duplicate.csv'):
        """ Use custom command to upload file and parse it into Items """
        self.command(filename)
        items = Item.objects.all().order_by('code_share')
        # Check a couple of the fields in Item    
        self.assertEqual(len(items), 3)
        codes = (u'bucket', u'tent', u'watercan')
        for i, item in enumerate(items):
            self.assertEqual(item.code_share, codes[i])
        Item.objects.all().delete()

    def test_number(self, filename='test_number.csv'):
        """ Use command to parse file with problem numeric fields 
            Missing field value, negative, fractions and too big
        """
        errs = [u'Column quantity = -23, less than zero so set to 0',
                u'Column quantity = 1e+28 more than the max integer 9223372036854775807',
                u'Column quantity = Not_a_Number is not a number so is set to 0',
                u'Column quantity = nan is not an integer so is set to 0',
                ]
        self.command(filename, expected_errs=errs)
        # check fractional numbers into integers
        items = Item.objects.filter(code_org='WA017')
        self.assertEqual(items[0].quantity, 33)
        # check empty values into zeros
        items = Item.objects.filter(code_org='WA041')
        self.assertEqual(items[0].quantity, 0)        
        # 9223372036854775807 is the reliable limit so this wont work
        # test is to ensure that 1e+28 error above is reported
        items = Item.objects.filter(code_org='RF028')
        self.assertNotEqual(items[0].quantity, 9999999999999999999999999999) 
        Item.objects.all().delete()

