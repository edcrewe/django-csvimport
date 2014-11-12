# -*- coding: utf-8 -*-
# Use unicode source code to make test character string writing easier
from csvimport.tests.testcase import CommandTestCase
from csvimport.tests.models import Item
import sys
pyversion = sys.version_info[0] # python 2 or 3

class CommandParseTest(CommandTestCase):
    """ Run test of file parsing """

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
        if pyversion == 2:
            self.assertEqual(unicode(item.uom), u'pi图e')
        else:
            self.assertEqual(str(item.uom), u'pi图e')            
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()

    def test_char2(self, filename='test_char2.csv'):
        """ Use custom command to parse file with range of unicode characters """
        self.command(filename)
        item = self.get_item(u"Cet élément est utilisé par quelqu'un d'autre et ne peux être modifié")
        self.assertEqual(item.description,
                         "TENTE FAMILIALE, 12 m_, COMPLETE (tapis de sol/double toit)")
        self.assertEqual(item.quantity, 101)
        if pyversion == 2:
            self.assertEqual(unicode(item.uom), u'删除当前图片')
        else:
            self.assertEqual(str(item.uom), '删除当前图片')
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()

    def test_duplicate(self, filename='test_duplicate.csv'):
        """ Use custom command to upload file and parse it into Items """
        self.deduplicate = True
        self.command(filename, expected_errs = ['Imported 3 rows to Item'])
        items = Item.objects.all().order_by('code_share')
        self.assertEqual(len(items), 3)
        # Check a couple of the fields in Item
        codes = (u'bucket', u'tent', u'watercan')
        for i, item in enumerate(items):
            self.assertEqual(item.code_share, codes[i])
        self.command(filename, expected_errs = ['Imported 6 rows to Item'], deduplicate=False)
        items = Item.objects.all().order_by('code_share')
        self.assertEqual(len(items), 3 + 6)
        Item.objects.all().delete()

    def test_number(self, filename='test_number.csv'):
        """ Use command to parse file with problem numeric fields
            Missing field value, negative, fractions and too big
        """
        errs = [u'row 0: Column quantity = -23, less than zero so set to 0',
                u'row 4: Column quantity = 1e+28 more than the max integer 9223372036854775807 sqlite may error with big integers so rounded down',
                u'row 5: Column quantity = Not_a_Number is not a number so is set to 0',
                u'row 6: Column quantity = nan is not an integer so is set to 0',
                ]
        self.command(csvfile=filename, expected_errs=errs)
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

    def test_quoted(self, filename='test_quoted.csv'):
        """ Use custom command parse file - test always double quote except some numbers 
            - test empty double quotes doesnt make the import skip a column """
        errs = ['Imported 3 rows to Item']
        self.command(filename, expected_errs=errs)
        item = self.get_item('heater')
        self.assertEqual(item.code_org, 'CWATCONT20F')
        self.assertEqual(item.status, 'Goods')
        self.assertEqual(item.quantity, 1000)
        self.assertEqual(item.organisation.name, 'AID-France')
        self.assertEqual(str(item.uom), 'pie')
        self.assertEqual(item.description, '')
        item = self.get_item('blanket')
        self.assertEqual(item.quantity, 0) # empty double quote
        self.assertEqual(item.status, 'Stock')
        item = self.get_item('shed')
        self.assertEqual(item.quantity, 180) 
        Item.objects.all().delete()
