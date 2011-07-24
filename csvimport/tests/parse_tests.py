from django.test import TestCase
#from utils import parse_excel_upload
import os

class CommandParseTest(TestCase):
    
    test_upload_path = 'fixtures/test_upload.xls'
    
    def test_parse(self):
      self.parse(self.test_upload_path)
