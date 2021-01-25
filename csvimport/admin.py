import locale
from datetime import datetime
from django import forms
from django.db import models
from django.contrib import admin
from django.contrib.admin import ModelAdmin

from csvimport.models import CSVImport


class CSVImportAdmin(ModelAdmin):
    """ Custom model to not have much editable! """

    readonly_fields = ["file_name", "upload_method", "error_log_html", "import_user"]
    fields = [
        "model_name",
        "field_list",
        "upload_file",
        "file_name",
        "delimiter",
        "encoding",
        "upload_method",
        "error_log_html",
        "import_user",
    ]
    formfield_overrides = {
        models.CharField: {"widget": forms.Textarea(attrs={"rows": "1", "cols": "40"})},
    }

    def get_changeform_initial_data(self, request):
        #This works for my problem, but I don't know if there are side effects. So I won't push it
        #locale.setlocale(locale.LC_ALL, '')
        return {'delimiter': ";" if locale.localeconv()['decimal_point'] == "," else ","}

    def save_model(self, request, obj, form, change):
        """ Do save and process command - cant commit False
            since then file wont be found for reopening via right charset
        """
        form.save()
        from csvimport.management.commands.importcsv import Command

        cmd = Command()
        if obj.upload_file:
            obj.file_name = obj.upload_file.name
            defaults = self.filename_defaults(obj.file_name)
            cmd.setup(
                mappings=obj.field_list,
                modelname=obj.model_name,
                charset=obj.encoding,
                uploaded=obj.upload_file,
                defaults=defaults,
                delimiter=obj.delimiter,
            )
        errors = cmd.run(logid=obj.id)
        if errors:
            obj.error_log = "\n".join(errors)
        obj.import_user = str(request.user)
        obj.import_date = datetime.now()
        obj.save()

    def filename_defaults(self, filename):
        """ Override this method to supply filename based data """
        defaults = []
        splitters = {"/": -1, ".": 0, "_": 0}
        for splitter, index in splitters.items():
            if filename.find(splitter) > -1:
                filename = filename.split(splitter)[index]
        return defaults


admin.site.register(CSVImport, CSVImportAdmin)
from csvimport.tests.models import Item

admin.site.register(Item)
