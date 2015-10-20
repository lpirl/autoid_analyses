from django.contrib import admin

from . import models

site = admin.site

site.site_header = 'AutoID administration'
site.site_title = site.site_header

site.register(models.Tag)
site.register(models.Scanner)
site.register(models.RCCarScan)
