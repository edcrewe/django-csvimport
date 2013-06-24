# -*- coding: utf-8 -*-
# Use unicode source code to make test character string writing easier
import os

from csvimport.management.commands.csvimport import CSVIMPORT_LOG
from django.conf import settings
from django.test import TestCase

class LogTest(TestCase):
    """ Run test of file parsing """
    logpath = ''

    def get_log_path(self):
        """ Get the log file that should of been written by the parse tests """
        if CSVIMPORT_LOG != 'logger':
            print '''CSVIMPORT_LOG is not set to 'logger' in settings 
                     - assume not using csvimport.tests.settings 
                     - so cannot test the log'''
            return False
        logging = getattr(settings, 'LOGGING', '')
        if logging:
            handlers = logging.get('handlers', {})
            if handlers:
                logfile = handlers.get('logfile',{})
                if logfile:
                    self.logpath = logfile.get('filename', '')
        if self.logpath.endswith('.log'):
           if os.path.exists(self.logpath):
               print 'Found csvimport_test.log'
               return True
        print '''cvsimport logging is not set up for %s from 
                 csvimport.tests.settings so cannot test the log''' % self.logpath
        return False

    def test_log(self):
        """ Check the log is there and then remove it """
        if self.get_log_path():
            csvlog = open(self.logpath)
            lines = csvlog.read()
            self.assertIn('Column quantity = -23, less than zero so set to 0', lines)
            os.remove(self.logpath)
            print 'Deleted csvimport_test.log'
        return
