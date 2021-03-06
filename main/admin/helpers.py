#encoding: utf8
from django.contrib import admin
from django.db.models import ForeignKey, DateTimeField
from django import forms

from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from main.utils import getattrs

def get_RFID_component_list_filter(attr_name):
  """
  Returns a ListFilter, configured for a related model found via
  ``attr_name``.
  """

  class ForeignKeyListFilter(admin.SimpleListFilter):
    """
    A list filter for a specific attribute. That attribute, in turn, has
    to be a relation to another model.
    """

    def lookups(self, request, model_admin):
      """
      Returns a list of tuples. The first element in each
      tuple will appear in the URL query (the PK of the related model).
      The second element is the human-readable name for the option that
      will appear in the right sidebar on the admin page (``str(obj)``).
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
      Returns the filtered ``queryset`` based on the value specified in
      the query string.
      I.e., only objects having a relation the the specified related
      object.
      """
      value = self.value()
      if not value:
        return queryset
      filter_kwargs =  {"%s_id" % attr_name: value}
      return queryset.filter(**filter_kwargs)

  # Human-readable title which will be displayed in the
  # right admin sidebar just above the filter options.
  ForeignKeyListFilter.title = attr_name

  # Parameter for the filter that will be used in the URL query.
  ForeignKeyListFilter.parameter_name = attr_name

  return ForeignKeyListFilter

def register_with_import_export(site, model_cls, exclude_model_attrs=tuple(),
                                id_fields=('pk',), search_fields=None,
                                list_filter=None, list_display=None):
  """
  Registers ``models_cls`` with a corresponding admin at ``site``.

  The corresponding admin has the ability to import and export data.
  Attributes to exclude from import and export can be specified via
  ``exclude_model_attrs``.
  For duplicate detection upon import, the attribute ``pk`` is used by
  default.
  If you want to use another (set of) attribute(s), you can specify them
  via ``id_fields``.

  The optional arguments ``search_fields``, ``list_filter`` and
  ``list_display`` are passed to the created admin.
  See
  https://docs.djangoproject.com/en/1.8/ref/contrib/admin/#modeladmin-options
  for details.
  """

  class Resource(ModelResource):
    """
    A resource similar to ``ModelResource`` but creates objects that
    are referenced in the data to be imported but that are missing in
    the database.

    Additionally, this resource carries configuration options in its
    contained class ``Meta``.
    """

    class Meta:
      model = model_cls
      exclude = exclude_model_attrs
      import_id_fields = id_fields
      skip_unchanged = True
      report_skipped = True

    # TODO: wire newly created scans with "Import" model, probably by
    #   overriding Resource.before_save_instance(instance, dry_run)

    def before_import(self, dataset, dry_run, **kwargs):
      """
      Creates missing related objects.

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
    """
    An admin with the ability import/export data.
    Additionally to some static configuration, it contains the
    configuration specified to ``register_with_import_export``.
    """
    resource_class = Resource
    skip_admin_log = True
    formfield_overrides = {
      DateTimeField: {
        'widget': forms.SplitDateTimeWidget(
          time_format='%H:%M:%S.%f'
        )
      },
    }

  # set some attributes based on arguments:
  if search_fields:
    Admin.search_fields = search_fields
  if list_display:
    Admin.list_display = list_display
    Admin.list_display_links = list_display
  if list_filter:
    Admin.list_filter = list_filter

  site.register(model_cls, Admin)
