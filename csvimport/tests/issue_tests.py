# -*- coding: utf-8 -*-
# Use unicode source code to make test character string writing easier
from csvimport.tests.testcase import CommandTestCase
from csvimport.tests.models import Issue98
import sys


class RegressionTest(CommandTestCase):
    """ Run tests with data from reported issue that last col is empty in github bug tracker 
        Could not replicate - all fields are populated without any trailing comma needed
    """

    def test_issue_98(self, filename="issue98.csv"):
        """ Test if last column is lost - check all rows and all values of a sample row"""
        info = ["Imported 5 rows to Issue98"]
        testrow = [
            "abcd190",
            "Data Science",
            2,
            "San Francisco",
            "Data Analyst",
            2,
            "San Francisco",
            "$92,000",
            "$106,000",
            "$121,500",
            "$13,000",
            "$15,600",
            "$18,720",
            "15%",
            "15%",
            "15%",
            "$118,800",
            "$137,500",
            "$158,445",
        ]
        self.command(filename, "csvimport.Issue98", bulk=True, expected_errs=info)
        objs = Issue98.objects.all()
        self.assertEqual(len(objs), 5)
        for obj in objs:
            self.assertTrue(len(obj.co_total_comp_high) > 6)
        obj = Issue98.objects.get(co_level=2)
        fields = Issue98._meta.get_fields()
        for i, field in enumerate(fields):
            self.assertEqual(getattr(obj, field.name), testrow[i])
