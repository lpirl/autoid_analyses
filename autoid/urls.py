"""autoid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
  https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
  1. Add an import:  from my_app import views
  2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
  1. Add an import:  from other_app.views import Home
  2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
  1. Add an import:  from blog import urls as blog_urls
  2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.utils.text import slugify

from main import views, admin, models

def generic_analyses_patterns(scan_cls):
  cls_name = scan_cls.__name__
  attr_names = ('tag', 'scanner')
  slug = slugify(scan_cls._meta.verbose_name_plural)
  return url(r'^%s/' % slug, include([
    url(
      r'%s-popularity/$' % attr_name,
      views.popularity,
      name="%s %s popularity" % (cls_name, attr_name),
      kwargs={"cls": scan_cls, "attr_name": attr_name}
    )
    for attr_name in attr_names
  ]))

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^admin/', include(admin.site.urls)),
  generic_analyses_patterns(models.RCCarScan),
  generic_analyses_patterns(models.ActivityAreaScan),
]
