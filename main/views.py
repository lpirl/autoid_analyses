# encoding: utf8
from collections import OrderedDict
import calendar

from django.shortcuts import render
from django.db.models import Max, Min

from main.utils import get_friendly_name_for_attr
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
    attrs_scan_count = OrderedDict(
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

def day_of_the_week_scan_count(request, cls):
  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  # ensure every day of the week is present and in correct order:
  counts = OrderedDict((d, 0) for d in calendar.day_name)

  counts.update(
    cls.get_timestamp_aggregated_scan_counts(
      lambda dt: dt.strftime("%A"),
      queryset
    )
  )

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": ("weekday",),
    "attrs_scan_count": counts,
    "datetime_range_form": datetime_range_form,
  }

  return render(request, 'scan_count_1_attr.html', context)

def hour_of_the_day_scan_count(request, cls):
  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  # ensure every hour of the day is present and in correct order:
  counts = OrderedDict((d, 0) for d in range(23))

  counts.update(
    cls.get_timestamp_aggregated_scan_counts(
      lambda dt: dt.hour,
      queryset
    )
  )

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": ("hour of the day",),
    "attrs_scan_count": counts,
    "datetime_range_form": datetime_range_form,
  }

  return render(request, 'scan_count_1_attr.html', context)

def month_of_the_year_scan_count(request, cls):
  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  # ensure every month of the year is present and in correct order:
  counts = OrderedDict((d, 0) for d in calendar.month_name[1:])

  import pdb
  pdb.set_trace()

  counts.update(
    cls.get_timestamp_aggregated_scan_counts(
      lambda dt: dt.strftime("%B"),
      queryset
    )
  )

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": ("month of the year",),
    "attrs_scan_count": counts,
    "datetime_range_form": datetime_range_form,
  }

  return render(request, 'scan_count_1_attr.html', context)
