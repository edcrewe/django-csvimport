from django.contrib import admin
from csvimport.tests.models import Country, UnitOfMeasure, Organisation, Item

admin.site.register(Country)
admin.site.register(UnitOfMeasure)
admin.site.register(Organisation)
admin.site.register(Item)
