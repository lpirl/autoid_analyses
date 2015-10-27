from django.conf.urls import include, url
from django.utils.text import slugify

from main import views, admin, models

def generic_analyses_patterns(scan_cls):
  cls_name = scan_cls.__name__
  slug = slugify(scan_cls._meta.verbose_name_plural)
  return url(r'^%s/' % slug, include([
    url(
      r'^tag-scan-count/$',
      views.related_attrs_scan_count,
      name="%s tag-scan-count" % cls_name,
      kwargs={"cls": scan_cls, "attr_names": ("tag",)}
    ),
    url(
      r'^scanner-scan-count/$',
      views.related_attrs_scan_count,
      name="%s scanner-scan-count" % cls_name,
      kwargs={"cls": scan_cls, "attr_names": ("scanner",)}
    ),
    url(
      r'^tag-scanner-scan-count/$',
      views.related_attrs_scan_count,
      name="%s tag-scanner-scan-count" % cls_name,
      kwargs={"cls": scan_cls, "attr_names": ("tag", "scanner")}
    ),
    url(
      r'^scan-intervals/$',
      views.related_attr_scan_intervals,
      name="%s scan-intervals" % cls_name,
      kwargs={"cls": scan_cls, "attr_name": "tag"}
    ),
  ]))

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  generic_analyses_patterns(models.RCCarScan),
  generic_analyses_patterns(models.ActivityAreaScan),
  generic_analyses_patterns(models.VideoScan),
  generic_analyses_patterns(models.WorkstationLoginScan),
]
