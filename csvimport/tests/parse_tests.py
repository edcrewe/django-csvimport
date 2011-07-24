import os

from django.test import TestCase
from csvimport.management.commands.csvimport import Command

class DummyFileObj:
    path = ''

    def set_path(self, filename):
        self.path = os.path.join(os.path.dirname(__file__), 
                                 'fixtures',
                                 filename)

class CommandParseTest(TestCase):
    """ Run test of file parsing """

    def test_parse(self, filename='test.csv'):
        cmd = Command()
        uploaded = DummyFileObj()
        uploaded.set_path(filename)
        cmd.setup(mappings='', 
                  modelname='csvtest.Item', 
                  uploaded=uploaded,
                  defaults='')
        errors = cmd.run(logid='commandtest')
        print errors
