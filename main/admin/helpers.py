#encoding: utf8
from django.contrib import admin
from django.db.models import ForeignKey, DateTimeField
from django import forms

from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from main.utils import getattrs

def get_RFID_component_list_filter(attr_name):
  class RFIDComponentListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
      """
      Returns a list of tuples. The first element in each
      tuple is the coded value for the option that will
      appear in the URL query. The second element is the
      human-readable name for the option that will appear
      in the right sidebar.
      """
      scans = model_admin.resource_class._meta.model.objects.only(
        "%s_id" % attr_name, attr_name
      ).distinct(
      ).select_related(
        attr_name
      )
      components = set(getattrs(scans, attr_name))
      return [(getattr(c, "pk", None), str(c)) for c in components]

    def queryset(self, request, queryset):
      """
      Returns the filtered queryset based on the value
      provided in the query string.
      """
      value = self.value()
      if not value:
        return queryset
      filter_kwargs =  {"%s_id" % attr_name: value}
      return queryset.filter(**filter_kwargs)

  # Human-readable title which will be displayed in the
  # right admin sidebar just above the filter options.
  RFIDComponentListFilter.title = attr_name

      # Parameter for the filter that will be used in the URL query.
  RFIDComponentListFilter.parameter_name = attr_name

  return RFIDComponentListFilter

def register_with_import_export(site, model_cls, exclude_model_attrs=tuple(),
                                id_fields=('pk',), search_fields=None,
                                list_filter=None, list_display=None):

  class Resource(ModelResource):

    class Meta:
      model = model_cls
      exclude = exclude_model_attrs
      import_id_fields = id_fields
      skip_unchanged = True
      report_skipped = True

    # TODO: wire with "Import" model

    def before_import(self, dataset, dry_run, **kwargs):
      """
      Creates required but missing related objects.

      Thanks to the setting ``IMPORT_EXPORT_USE_TRANSACTIONS``, the
      objects created herein are not actually kept when called for an
      import preview.
      """
      for field_name in dataset.headers:
        field = model_cls._meta.get_field(field_name)
        if type(field) is not ForeignKey:
          continue
        related_model_cls = field.related_model().__class__
        required_pks = set(dataset[field_name])
        existing_pks = set(
          related_model_cls.objects.all().values_list('pk', flat=True)
        )
        missing_objects = [
          related_model_cls(pk=pk) for pk in required_pks - existing_pks
        ]
        related_model_cls.objects.bulk_create(missing_objects)

  class Admin(ImportExportModelAdmin):
    resource_class = Resource
    skip_admin_log = True
    formfield_overrides = {
      DateTimeField: {
        'widget': forms.SplitDateTimeWidget(
          time_format='%H:%M:%S.%f'
        )
      },
    }

  if search_fields:
    Admin.search_fields = search_fields
  if list_display:
    Admin.list_display = list_display
    Admin.list_display_links = list_display
  if list_filter:
    Admin.list_filter = list_filter

  site.register(model_cls, Admin)
