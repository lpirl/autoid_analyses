from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from . import models

site = admin.site

site.site_header = 'AutoID administration'
site.site_title = 'AutoID administration'
site.index_title = 'Data administration'

def register_with_import_export(model_cls, exclude_model_attrs=tuple()):

  class Resource(ModelResource):

    class Meta:
        model = model_cls
        exclude = exclude_model_attrs

  class ModelScanAdmin(ImportExportModelAdmin):
    resource_class = Resource

  site.register(model_cls, ModelScanAdmin)

register_with_import_export(models.Tag)
register_with_import_export(models.Scanner)
register_with_import_export(models.RCCarScan, ("id",))
