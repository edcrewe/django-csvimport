# -*- coding: utf-8 -*-
# Use unicode source code to make test character string writing easier
from csvimport.tests.testcase import CommandTestCase
from csvimport.tests.models import Country
import sys
import timeit
from django.core.exceptions import ObjectDoesNotExist

pyversion = sys.version_info[0]  # python 2 or 3


class PerformanceTest(CommandTestCase):
    """ Run test of file parsing """

    def test_time_load(self, filename='countries.csv'):
        """Time the upload of a country file"""
        errs = ['Imported 246 rows to Country']
        time = self.command(csvfile=filename, modelname='csvimport.Country', defaults='',
                     expected_errs=errs,
                     clean=False,
                     time=True)
        self.assertTrue(time < 0.4)
        print "Time to run coutnries import was %s" % time
        self.assertTrue(Country.objects.count()>240)
        Country.objects.all().delete()
