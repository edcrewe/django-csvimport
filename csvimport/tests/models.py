# Test case models for cvsimport - add 'csvimport.tests' to installed apps to run
from django.db import models

class Issue98(models.Model):
    ''' Autogenerated model file csvimportissue98 Sun May  3 11:00:37 2020 '''

    co_id = models.CharField(max_length=7, primary_key=True, blank=False, null=False, default='')
    co_role = models.CharField(max_length=16, blank=True, null=True)
    co_level = models.IntegerField(blank=True, null=True, default=0)
    co_region = models.CharField(max_length=16, blank=True, null=True)
    tm_role = models.CharField(max_length=16, blank=True, null=True)
    tm_level = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, default=0)
    tm_region = models.CharField(max_length=16, blank=True, null=True)
    co_salary_low = models.CharField(max_length=8, blank=True, default='')
    co_salary_mid = models.CharField(max_length=8, blank=True, default='')
    co_salary_high = models.CharField(max_length=8, blank=True, default='')
    co_equity_low = models.CharField(max_length=8, blank=True, default='')
    co_equity_mid = models.CharField(max_length=8, blank=True, default='')
    co_equity_high = models.CharField(max_length=8, blank=True, default='')
    co_bonus_low = models.CharField(max_length=3, blank=True, default='')
    co_bonus_mid = models.CharField(max_length=3, blank=True, default='')
    co_bonus_high = models.CharField(max_length=3, blank=True, default='')
    co_total_comp_low = models.CharField(max_length=8, blank=True, default='')
    co_total_comp_mid = models.CharField(max_length=8, blank=True, default='')
    co_total_comp_high = models.CharField(max_length=8, blank=True, default='')

    class Meta:
        managed = False
        db_table = u'"issue98"'

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
        app_label = u"csvimport"
        db_table = u'"csvtests_country"'
        managed = True

    def __str__(self):
        return u"%s (%s)" % (self.name, self.code)


class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        app_label = u"csvimport"
        db_table = u"csvtests_unitofmeasure"
        managed = True

    def __str__(self):
        return self.name


class Organisation(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        app_label = u"csvimport"
        db_table = u"csvtests_organisation"
        managed = True


class Item(models.Model):
    TYPE = models.PositiveIntegerField(default=0)
    code_share = models.CharField(
        max_length=32, help_text="Cross-organization item code"
    )
    code_org = models.CharField(
        max_length=32, help_text="Organization-specfific item code"
    )
    description = models.TextField(null=True)
    quantity = models.PositiveIntegerField(default=1)
    uom = models.ForeignKey(
        UnitOfMeasure, on_delete=models.CASCADE, help_text="Unit of Measure"
    )
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, null=True)
    date = models.DateField(auto_now=True, null=True, validators=[])
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)

    class Meta:
        app_label = u"csvimport"
        db_table = u"csvtests_item"
        managed = True

    def __str__(self):
        return self.description
