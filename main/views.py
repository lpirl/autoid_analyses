# encoding: utf8
from django.shortcuts import render

from main.utils import (getattrs, HierarchicalOrderedDict,
                        get_verbose_name_plural_for_attr)

def index(request):
  return render(request, 'index.html', {})

def related_attrs_popularity(request, cls, attr_names):

  attr_verbose_names = [
    get_verbose_name_plural_for_attr(cls, n)
    for n in attr_names
  ]

  attrs_popularity = cls.get_related_attrs_popularity(attr_names)

  attrs_count = len(attr_names)
  if attrs_count == 1:
    attrs_popularity = HierarchicalOrderedDict(
      sorted(
        attrs_popularity.iteritems(),
        key=lambda t: t[1][0],
        reverse=True
      )
    )
    template = 'popularity_1_attr.html'
  elif attrs_count == 2:
    template = 'popularity_2_attrs.html'
  else:
    raise NotImplementedError("View can only handle one or two attributes.")

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": attr_verbose_names,
    "attrs_popularity": attrs_popularity,
  }

  return render(request, template, context)

def related_attr_scan_intervals(request, cls, attr_name):

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_name": get_verbose_name_plural_for_attr(cls, attr_name),
    "series": cls.get_related_attr_scan_intervals(attr_name),
  }

  return render(request, "scan_intervals.html", context)
