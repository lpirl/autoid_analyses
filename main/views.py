# encoding: utf8
from django.shortcuts import render
from django.db.models import Max, Min, Count

from main.utils import (getattrs, HierarchicalOrderedDict,
                        get_friendly_name_for_attr,
                        values_to_hierarchical_dict)
from forms import DateTimeRangeForm

def index(request):
  return render(request, 'index.html', {})

def _get_form_and_queryset(request, cls):
  queryset = cls.objects

  initial_form_data = cls.objects.aggregate(
    from_datetime=Min('timestamp'), to_datetime=Max('timestamp')
  )

  datetime_range_form = DateTimeRangeForm(
    request.GET or None,
    initial=initial_form_data
  )

  if datetime_range_form.is_valid():
    from_datetime = datetime_range_form.cleaned_data["from_datetime"]
    to_datetime = datetime_range_form.cleaned_data["to_datetime"]
    queryset= queryset.filter(
      timestamp__range=(from_datetime, to_datetime)
    )

  return (datetime_range_form, queryset)

def related_attrs_scan_count(request, cls, attr_names):

  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  attr_verbose_names = [
    get_friendly_name_for_attr(cls, n)
    for n in attr_names
  ]

  attrs_scan_count = cls.get_related_attrs_scan_count(attr_names,
                                                      queryset=queryset)

  attrs_count = len(attr_names)
  if attrs_count == 1:
    attrs_scan_count = HierarchicalOrderedDict(
      sorted(
        attrs_scan_count.iteritems(),
        key=lambda t: t[1],
        reverse=True
      )
    )
    template = 'scan_count_1_attr.html'
  elif attrs_count == 2:
    template = 'scan_count_2_attrs.html'
  else:
    raise NotImplementedError("View can only handle one or two attributes.")

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": attr_verbose_names,
    "attrs_scan_count": attrs_scan_count,
    "datetime_range_form": datetime_range_form,
  }

  return render(request, template, context)

def related_attr_scan_intervals(request, cls, attr_name):

  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_name": get_friendly_name_for_attr(cls, attr_name),
    "series": cls.get_related_attr_scan_intervals(attr_name, queryset=queryset),
    "datetime_range_form": datetime_range_form,
  }

  return render(request, "scan_intervals.html", context)

def related_attrs_scan_count_per_weekday(request, cls):
  # TODO: needs heavy refactoring

  TIMESTAMP_ATTR_NAME = "timestamp"
  WEEKDAY_ATTR_NAME = "weekday"

  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  counts_values = queryset.extra(
    select={WEEKDAY_ATTR_NAME: 'strftime("%%w", %s)' % TIMESTAMP_ATTR_NAME}
  ).values(
    WEEKDAY_ATTR_NAME
  ).annotate(
    count=Count("pk")
  ).order_by(
    WEEKDAY_ATTR_NAME
  )

  WEEKDAYS = {
    0: "Sundays",
    1: "Mondays",
    2: "Tuesdays",
    3: "Wednesdays",
    4: "Thursdays",
    5: "Fridays",
    6: "Saturdays",
  }

  counts_raw = values_to_hierarchical_dict(counts_values, (WEEKDAY_ATTR_NAME,))
  counts = {}
  for weekday_num, count_dict in counts_raw.iteritems():
    weekday_name = WEEKDAYS[int(weekday_num)]
    counts[weekday_name] = count_dict["count"]

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": ("weekday",),
    "attrs_scan_count": counts,
    "datetime_range_form": datetime_range_form,
  }

  return render(request, 'scan_count_1_attr.html', context)
