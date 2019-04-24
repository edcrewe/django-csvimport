# -*- coding: utf-8 -*-
# Use unicode source code to make test character string writing easier
from csvimport.tests.testcase import CommandTestCase
from csvimport.tests.models import Country
import sys
from django.core.exceptions import ObjectDoesNotExist

pyversion = sys.version_info[0]  # python 2 or 3


class ConstraintTest(CommandTestCase):
    """ Run test of file parsing """

    def get_country(self, country_code):
        try:
            country = Country.objects.get(code__exact=country_code)
        except ObjectDoesNotExist:
            country = None
            self.assertTrue(
                country, "Failed to get row from imported test csv for countries"
            )
        return country

    def test_empty_notnull(self, filename="bad_country.csv"):
        """ Use custom command to upload a country file with missing long lat data"""
        errs = [
            "could not convert string to float: 'null'",
            "could not convert string to float: 'null'",
            "Imported 3 rows to Country",
        ]

        self.command(
            csvfile=filename,
            modelname="csvimport.Country",
            defaults="",
            expected_errs=errs,
            clean=False,
        )
        self.assertEqual(Country.objects.count(), 3)
        country = self.get_country("K1")
        self.assertTrue(country.name, "Montserrat")
        Country.objects.all().delete()
