# encoding: utf8
from django.shortcuts import render
from django.db.models import Max, Min
from django.views.decorators.csrf import csrf_exempt

from main.utils import (getattrs, HierarchicalOrderedDict,
                        get_verbose_name_plural_for_attr)
from forms import DateTimeRangeForm

def index(request):
  return render(request, 'index.html', {})

@csrf_exempt
def related_attrs_popularity(request, cls, attr_names):

  queryset = cls.objects

  initial_form_data = cls.objects.aggregate(
    from_datetime=Min('timestamp'), to_datetime=Max('timestamp')
  )

  date_time_range_form = DateTimeRangeForm(
    request.GET or None,
    initial = initial_form_data
  )
  if date_time_range_form.is_valid():
    from_datetime = date_time_range_form.cleaned_data["from_datetime"]
    to_datetime = date_time_range_form.cleaned_data["to_datetime"]
    queryset= queryset.filter(
      timestamp__range=(from_datetime, to_datetime)
    )

  attr_verbose_names = [
    get_verbose_name_plural_for_attr(cls, n)
    for n in attr_names
  ]

  attrs_popularity = cls.get_related_attrs_popularity(attr_names,
                                                      queryset=queryset)

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
    "date_time_range_form": date_time_range_form,
  }

  return render(request, template, context)

def related_attr_scan_intervals(request, cls, attr_name):

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_name": get_verbose_name_plural_for_attr(cls, attr_name),
    "series": cls.get_related_attr_scan_intervals(attr_name),
  }

  return render(request, "scan_intervals.html", context)
