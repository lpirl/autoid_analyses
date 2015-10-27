from django.contrib import admin

from main import models
from . import helpers

site = admin.site
site.site_header = 'AutoID administration'
site.site_title = 'AutoID administration'
site.index_title = 'Data administration'

register_component_kwargs = {
  "search_fields": ("component_id", "friendly_name", "comments"),
  "list_display": ("component_id", "friendly_name", "comments"),
}
helpers.register_with_import_export(site, models.Tag,
                                    **register_component_kwargs)
helpers.register_with_import_export(site, models.Scanner,
                                    **register_component_kwargs)

register_scan_kwargs = {
  "exclude_model_attrs": ("id",),
  "id_fields": ("timestamp", "tag"),
  "list_display": ("timestamp", "tag", "scanner"),
  "list_filter": (
    "timestamp",
    helpers.get_RFID_component_list_filter("tag"),
    helpers.get_RFID_component_list_filter("scanner")
  ),
}
helpers.register_with_import_export(site, models.RCCarScan,
                                    **register_scan_kwargs)
helpers.register_with_import_export(site, models.ActivityAreaScan,
                                    **register_scan_kwargs)
helpers.register_with_import_export(site, models.VideoScan,
                                    **register_scan_kwargs)
