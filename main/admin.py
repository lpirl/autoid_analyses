from django.contrib import admin

from main import models

admin.site.register(models.Tag)
admin.site.register(models.Scanner)
admin.site.register(models.RCCarScan)
