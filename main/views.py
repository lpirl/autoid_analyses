# encoding: utf8
from collections import OrderedDict
import calendar

from django.shortcuts import render
from django.db.models import Max, Min

from main.utils import get_friendly_name_for_attr
from forms import DateTimeRangeForm

def index(request):
  """
  Renders the index page. Nothing special here.
  """
  return render(request, 'index.html', {})

def _get_form_and_queryset(request, cls):
  """
  For the given ``cls`` this method creates or processes a form to
  specify date boundaries (to, from).
  If specified, this date boundaries are used to limit the objects of
  ``cls``.
  The form, as well as the possibly limited queryset are returned as a
  tuple.
  """
  queryset = cls.objects

  # get Min and Mix timestamp for reasonable form presets
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
  """
  Renders a view that displays the scan counts for the combinations of
  attributes specified via ``attr_names``.

  That is, all existing values of all ``attr_names`` are extracted from
  the objects of ``cls``.
  For all possible combinations of those values (think n-dimensional
  matrix), the number of existing scans with that particular combination
  of values is counted.

  Currently, ``attr_names`` can only contain one or two attribute names:
  For one attribute name, the scan counts are displayed relatively
  (pie chart) and absolutely (bar chart).
  For two attribute names, the scan counts are displayed in a
  table/heatmap.
  """

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
  """
  View renders a line chart that displays the scan interval for objects
  of ``cls``.
  The scan intervals are grouped by all possible
  values of ``attr_name`` (i.e. made to "data series").

  See ``related_attrs_scan_count`` for details about the grouping.
  """

  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_name": get_friendly_name_for_attr(cls, attr_name),
    "series": cls.get_related_attr_scan_intervals(attr_name, queryset=queryset),
    "datetime_range_form": datetime_range_form,
  }

  return render(request, "scan_intervals.html", context)

def day_of_the_week_scan_count(request, cls):
  """
  View displays the relative count (pie chart) and the absolute count
  (bar chart) of objects of ``cls``, grouped by days of the week.

  I.e. count all scans that happened on a Monday, on a Tuesday, etc.
  """
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
  """
  View displays the relative count (pie chart) and the absolute count
  (bar chart) of objects of ``cls``, grouped by hour of the day.

  I.e. count all scans that happened 00-01 am, 01-02 am, etc.
  """
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
  """
  View displays the relative count (pie chart) and the absolute count
  (bar chart) of objects of ``cls``, grouped by month of the year.

  I.e. count all scans that happened in January, February, etc.
  """
  datetime_range_form, queryset = _get_form_and_queryset(request, cls)

  # ensure every month of the year is present and in correct order:
  counts = OrderedDict((d, 0) for d in calendar.month_name[1:])

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
