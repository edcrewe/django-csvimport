# Test case models for cvsimport - add 'csvimport.tests' to installed apps to run
from django.db import models


class Country(models.Model):
    """
    ISO country (location) codes.
    and lat long for Geopoint Mapping
    """
    code = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, default=0)
    longitude = models.FloatField(null=True, default=0)
    alias = models.CharField(max_length=255, null=True)

    class Meta:
        app_label = u'csvimport'
        db_table = u'"csvtests_country"'
        managed = True

    def __str__(self):
        return u"%s (%s)" % (self.name, self.code)


class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        app_label = u'csvimport'
        db_table = u'csvtests_unitofmeasure'
        managed = True

    def __str__(self):
        return self.name


class Organisation(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        app_label = u'csvimport'
        db_table = u'csvtests_organisation'
        managed = True


class Item(models.Model):
    TYPE = models.PositiveIntegerField(default=0)
    code_share = models.CharField(
        max_length=32,
        help_text="Cross-organization item code")
    code_org = models.CharField(
        max_length=32,
        help_text="Organization-specfific item code")
    description = models.TextField(null=True)
    quantity = models.PositiveIntegerField(default=1)
    uom = models.ForeignKey(UnitOfMeasure,
                            help_text='Unit of Measure')
    organisation = models.ForeignKey(Organisation)
    status = models.CharField(max_length=10, null=True)
    date = models.DateField(auto_now=True, null=True, validators=[])
    country = models.ForeignKey(Country, null=True)

    class Meta:
        app_label = u'csvimport'
        db_table = u'csvtests_item'
        managed = True

    def __str__(self):
        return self.description
