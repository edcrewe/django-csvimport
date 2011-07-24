import os

from django.test import TestCase
from csvimport.management.commands.csvimport import Command

class CommandParseTest(TestCase):
    """ Run test of file parsing """
    test_upload_path = 'fixtures/test.csv'
    
    def test_parse(self):
        cmd = Command()
        test_fh = os.open(self.test_upload_path)
        cmd.setup(mappings='', 
                  modelname='csvimport.tests.Item', 
                  uploaded=test_fh,
                  defaults='')
        errors = cmd.run(logid=obj.id)
        print errors
