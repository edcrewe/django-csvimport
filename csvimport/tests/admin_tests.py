# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from csvimport.tests.testcase import CommandTestCase
from csvimport.tests.models import Item
from csvimport.models import CSVImport, get_models


class AdminTest(CommandTestCase):
    """ Run test of csvimport admin UI """

    def test_get_models(self):
        """Check that get_models is working to give a list of models for import"""
        models = get_models()
        self.assertTrue(len(models) > 6)
        self.assertIn(("csvimport.Item", "csvimport.Item"), models)

    def test_admin(self):
        c = Client()
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual(CSVImport.objects.count(), 0)
        self.user = User.objects.create_superuser(
            "admin", "admin@example.com", "letmein"
        )
        login = c.login(username="admin", password="letmein")
        fixpath = os.path.join(
            os.getcwd(), "src/django-csvimport/csvimport/tests/fixtures/test_plain.csv"
        )
        with open(fixpath) as fp:
            fake_file = ContentFile(fp.read())
            fake_file.name = "test_plain.csv"
            data = {
                "model_name": "csvimport.Item",
                "field_list": "CODE_SHARE,CODE_ORG,ORGANISATION,DESCRIPTION,UOM,QUANTITY,STATUS",
                "upload_file": fake_file,
                "encoding": "utf-8",
            }
            response = c.post("/admin/csvimport/csvimport/add/", data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "csvimport.Item is not one of the available choices", str(response.content)
        )
        self.assertNotIn("This field is required", str(response.content))
        self.assertEqual(CSVImport.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 9)
        return
