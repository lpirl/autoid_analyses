# encoding: utf8
from datetime import timedelta

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
        key=lambda t: t[1]["count"],
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
  TIMESTAMP_ATTR_NAME = "timestamp"
  TIMESTAMP_DELTA_KEY = "delta"

  objects = cls.objects.only(
    TIMESTAMP_ATTR_NAME, attr_name
  ).select_related(
    attr_name
  ).order_by(
    attr_name,
    TIMESTAMP_ATTR_NAME
  )

  # all_series: {attr_object -> [(timestamp, delta_to_last), …], …}
  all_series = {
    o: [] for o in set(getattrs(objects, attr_name))
  }
  for scan in objects:
    timestamp = scan.timestamp
    attr_object = getattr(scan, attr_name)
    inner_series = all_series.get(attr_object)
    if inner_series:
      last_timestamp = inner_series[-1][0]
      delta = timestamp - last_timestamp
    else:
      delta = timedelta()
    inner_series.append((timestamp, delta))

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_name": get_verbose_name_plural_for_attr(cls, attr_name),
    "series": all_series,
  }

  return render(request, "scan_intervals.html", context)
