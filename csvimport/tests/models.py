# Test case models for cvsimport - add 'csvimport.tests' to installed apps to run
from django.db import models

class Country(models.Model):
    """
    ISO country (location) codes.
    and lat long for Geopoint Mapping
    """
    code = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    alias = models.CharField(max_length=255, null=True)


    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code)


class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=32)


    def __unicode__(self):
        return self.name


class Organisation(models.Model):
    name = models.CharField(max_length=255)


    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'tests_organisation'
        managed = True


class Item(models.Model):
    TYPE = models.PositiveIntegerField(default=0)
    code_share = models.CharField(
        max_length=32,
        help_text = "Cross-organization item code")
    code_org = models.CharField(
        max_length=32,
        help_text="Organization-specfific item code")
    description = models.TextField(null=True)
    quantity = models.PositiveIntegerField(default=1)
    uom = models.ForeignKey(UnitOfMeasure,
                            help_text = 'Unit of Measure')
    organisation = models.ForeignKey(Organisation)
    status = models.CharField(max_length = 10, null=True)
    date = models.DateField(auto_now=True, null=True, validators=[])
    country = models.ForeignKey(Country)


