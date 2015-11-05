# encoding: utf8

from itertools import product
from datetime import timedelta

from django.db import models

from main.utils import (getattrs, values_to_hierarchical_dict,
                        HierarchicalOrderedDict)

# TODO: model "Import" to log what has been imported by who etc.
#       (mainly for easy of deletion)

class AbstractRFIDComponent(models.Model):
  """
  Represents a physical component involved in RFID scanning
  (i.e. scanner or tag).
  """

  class Meta:
    abstract = True

  component_id = models.CharField(max_length=64, primary_key=True,
      help_text="The ID that is used in imported data.")
  friendly_name = models.CharField(max_length=64, blank=True,
      help_text="Might be used to ease readability for humans.")
  comments = models.TextField(blank=True)

  def __unicode__(self):
    name = self.friendly_name or self.__class__.__name__
    return "%s (%s)" % (name, self.pk)

class Tag(AbstractRFIDComponent):
  """
  Represents a physical RFID tag.
  """
  pass

class Scanner(AbstractRFIDComponent):
  """
  Represents a physical RFID scanner.
  """
  pass

class AbstractScan(models.Model):
  """
  Represents a scan, i.e. a tag at a possibly known scanner.
  """

  class Meta:
    abstract = True
    unique_together = ("timestamp", "tag", "scanner")

  timestamp = models.DateTimeField(db_index=True)
  tag = models.ForeignKey("Tag")
  scanner = models.ForeignKey("Scanner", blank=True, null=True)

  def __unicode__(self):
    out = "%s at %s: %s" % (self.__class__.__name__, self.timestamp,
                                    self.tag)
    if self.scanner:
      out += " by %s" % self.scanner
    return out

  @classmethod
  def get_related_attrs_scan_count(cls, attr_names, queryset=None):
    """
    Calculates the total count for a combination of related attributes
    (``attr_names``).
    Results might be optionally limited using ``queryset``.

    Returns a ``len(attr_names)``-dimensional dict, one dimension
    per attribute name. Each leaf is a tuple with the count of the
    particular combination of attributes.

    Example:

      {
        <Tag: thriller>: {
          <Author: Stephen King>: 120
          },
          …
        },
        …
      },

    """
    objects = queryset or cls.objects
    objects = objects.select_related(*attr_names)

    # get a list (of dicts) with all object combinations and their counts
    attr_combinations_values = objects.values(
      *attr_names
    ).annotate(
      count=models.Count("pk")
    ).order_by(
    )

    # a list of object lists, needed to determine possible object
    # combinations
    attrs_objects = [
      set(getattrs(objects, attr_name)) for attr_name in attr_names
    ]

    # needed to lookup counts for certain object combinations
    counts_by_pk = values_to_hierarchical_dict(
      attr_combinations_values,
      attr_names
    )

    # needed to calculate percentiles (that's why it's already float)
    objects_count = float(len(objects))

    # if object combination does not exist, this information is provided:
    default_leaf = 0

    # assemble a complete hierarchical dictionary of possible
    # combinations of attributes, including their count and percentile
    out = HierarchicalOrderedDict()
    for combination in product(*attrs_objects):

      count_dict = counts_by_pk.get_by_path(
        (getattr(o, "pk", None) for o in combination),
        None
      )

      if count_dict:
        count = count_dict["count"]
      else:
        count = default_leaf
      out.set_by_path(combination, count)

    return out

  @classmethod
  def get_related_attr_scan_intervals(cls, attr_name, queryset=None):
    """
    Creates a series of time deltas between scans, grouped by objects
    found under ``attr_name``. Results might be optionally limited using
    ``queryset``.

    Returns a dict with the related object as key and a list of tuples
    as value. The tuples are filled with the timestamp and the
    ``timedelta`` to the previous scan.

    Example:

      {
        <Tag: thriller>: [
          (datetime(…), timedelta(…)),
          (datetime(…), timedelta(…)),
        ],
        …
      }
    """

    objects = queryset or cls.objects
    objects = objects.only(
      "timestamp", attr_name
    ).select_related(
      attr_name
    )

    # initialize with empty lists (avoids cumbersome checks below)
    attr_objects = objects.only(attr_name).distinct()
    all_series = {o: [] for o in getattrs(attr_objects, attr_name)}

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

    return all_series

  @classmethod
  def get_timestamp_aggregated_scan_counts(cls, aggregation_criterion_func,
                                          queryset=None):
    """
    Calculates the total count per aggregate for all scans.
    ``aggregation_criterion_func`` is invoked with a datetime object and
    its return value is used to determine which aggregate count increment.
    Results might be optionally limited using ``queryset``.

    Returns a dict, mapping the aggregates (return values of
    ``aggregation_criterion_func``) to their corresponding scan counts.

    Example result, count per day of month::

      {
        1: 2,
        2: 43,
        3: 12,
        …
        29: 4,
        30: 78,
        31: 33,
      },
    """
    queryset = queryset or cls.objects

    timestamps = queryset.values_list("timestamp", flat=True)
    criteria = [aggregation_criterion_func(t) for t in timestamps]
    count = criteria.count

    return {k: count(k) for k in set(criteria)}

class RCCarScan(AbstractScan):
  pass

class ActivityAreaScan(AbstractScan):
  pass

class VideoScan(AbstractScan):
  pass

class WorkstationLoginScan(AbstractScan):
  pass
