""" Test use of optional command line args """
from csvimport.tests.testcase import CommandTestCase
from csvimport.tests.models import Item


class CommandArgsTest(CommandTestCase):
    """ Run test of use of optional command line args - mappings, default and charset """

    def test_mappings(self, filename='test_headless.csv'):
        """ Use custom command to upload file and parse it into Items
            Handle either mapping format
            TODO: add handling of spaces in defaults?
        """
        # header equivalent only mapping
        mappings = 'CODE_SHARE,CODE_ORG,ORGANISATION,DESCRIPTION,UOM,QUANTITY,STATUS'
        # errs = ['Using manually entered mapping list']
        self.command(filename, mappings=mappings)  # , expected_errs=errs)
        item = self.get_item('sheeting')
        # Check a couple of the fields in Item
        self.assertEqual(item.code_org, 'RF007')
        self.assertEqual(item.description, 'Plastic sheeting, 4*60m, roll')
        # Check related Organisation model is created
        self.assertEqual(item.organisation.name, 'Save UK')
        Item.objects.all().delete()

        # full mapping
        mappings = '''column1=code_share,column2=code_org,
                    column3=organisation(Organisation|name),
                    column5=uom(UnitOfMeasure|name),column7=status'''
        defaults = 'country=KE(Country|code),quantity=5,description=stuff'
        errs = ['Using manually entered mapping list']
        self.command(filename, mappings=mappings, defaults=defaults, expected_errs=errs)
        item = self.get_item('sheeting')
        # Check a couple of the fields in Item
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.code_org, 'RF007')
        self.assertEqual(item.description, 'stuff')
        # Check related Organisation model is created
        self.assertEqual(item.organisation.name, 'Save UK')
        Item.objects.all().delete()

    def test_default(self, filename='test_char.csv'):
        """ Check the default values over-ride those in the file
            NB: Should we add an option to only make defaults change null values?
            ... maybe although all of that could be done post import anyway so
            this is more normally used to allow setting values for missing columns
        """
        defaults = 'code_org=ALLTHESAME,quantity=58'
        self.command(filename, defaults=defaults)
        item = self.get_item('watercan')
        self.assertNotEqual(item.code_org, 'CWATCONT20F')
        self.assertEqual(item.code_org, 'ALLTHESAME')
        self.assertNotEqual(item.quantity, 1000)
        self.assertEqual(item.quantity, 58)
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()
