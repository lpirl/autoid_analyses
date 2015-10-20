from django.contrib import admin

from . import models

site = admin.site

site.site_header = 'AutoID administration'
site.site_title = 'AutoID administration'
site.index_title = 'Data administration'

site.register(models.Tag)
site.register(models.Scanner)
site.register(models.RCCarScan)
