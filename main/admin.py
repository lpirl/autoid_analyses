from django.contrib import admin
from django.db.models import ForeignKey

from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from main import models

site = admin.site

site.site_header = 'AutoID administration'
site.site_title = 'AutoID administration'
site.index_title = 'Data administration'

def register_with_import_export(model_cls, exclude_model_attrs=tuple(),
                                id_fields=('pk',)):

  class Resource(ModelResource):

    class Meta:
      model = model_cls
      exclude = exclude_model_attrs
      import_id_fields = id_fields
      skip_unchanged = True
      report_skipped = True

    def before_import(self, dataset, dry_run, **kwargs):
      """
      Creates required but missing related objects.

      Thanks to the setting ``IMPORT_EXPORT_USE_TRANSACTIONS``, the
      objects created herein are not actually kept when called for an
      import preview.
      """
      for field_name in self.get_import_id_fields():

        # app import_export does not work without this assertion,
        # so we can assert it too:
        assert field_name in dataset.headers

        field = model_cls._meta.get_field(field_name)
        if type(field) is not ForeignKey:
          continue
        related_model_cls = field.related_model().__class__
        for related_pk in dataset[field_name]:
          related_model_cls.objects.get_or_create(pk=related_pk)

  class Admin(ImportExportModelAdmin):
    resource_class = Resource

  site.register(model_cls, Admin)

register_with_import_export(models.Tag)
register_with_import_export(models.Scanner)

register_scan_kwargs = {
  "exclude_model_attrs": ("id",),
  "id_fields": ("timestamp","tag"),
}
register_with_import_export(models.RCCarScan, **register_scan_kwargs)
