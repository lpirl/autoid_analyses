from collections import OrderedDict

class HierarchicalDictMixin(object):
  """
  Adds a few helpers for traversing down a hierarchy of dictionaries.
  """

  @staticmethod
  def _check_if_dict(obj):
    assert issubclass(type(obj), dict), \
        "Cannot traverse down hierarchical dict: %s is not a dict" % obj

  def set_by_path(self, keys_list, item):
    """
    Traverses down the hierarchy specified by ``keys_list`` and sets
    ``item``.
    """
    tmp = self
    for key in keys_list[:-1]:
      tmp = tmp.setdefault(key, self.__class__())
      self._check_if_dict(tmp)
    tmp[keys_list[-1]] = item

  def get_by_path(self, keys_list, default=None):
    """
    Traverses down the hierarchy specified by ``keys_list`` and returns
    last seed value.
    Uses ``default`` as default for getting values.
    """
    tmp = self
    for key in keys_list:
      self._check_if_dict(tmp)
      tmp = tmp.get(key, default)
    return tmp

class HierarchicalDict(dict, HierarchicalDictMixin):
  """
  Like ``dict``,  for traversing down a hierarchy of dictionaries.
  """
  pass

class HierarchicalOrderedDict(OrderedDict, HierarchicalDictMixin):
  """
  Like ``OrderedDict``,  for traversing down a hierarchy of dictionaries.
  """
  pass

def getattrs(objects, attr_name):
  """
  Like ``getattr`` but returns a list of attributes from all objects.
  """
  return [getattr(o, attr_name) for o in objects]

def values_to_hierarchical_dict(dicts, attr_names):
  """
  TODO: move to HierarchicalDictMixin

  Transforms a list of ``dicts`` (as returned by ``QuerySet.values()``)
  to a hierarchical dict, e.g. for easier lookup.
  The resulting hierarchy is determined by ``attr_names``: for every
  attribute name in there, a level hierarchy is created. E.g.:

    d = [
      {"foo": 11, "bar": 22, "x": 1, "y": 2},
      {"foo": 55, "bar": 66, "x": 1, "y": 5},
    ]
    values_to_hierarchical_dict(d, ("x", "y"))
    >>> {
      1: {
        2: {"foo": 11, "bar": 22},
        5: {"foo": 55, "bar": 66},
      },
    }

  """
  out = HierarchicalDict()
  for values in dicts:
    tmp_leaf = out
    for attr_name in attr_names:
      key = values.pop(attr_name)

      # create lower level if required and move down in the hierarchy
      tmp_leaf = tmp_leaf.setdefault(key, HierarchicalDict())

    # store remaining information when all the way down the hierarchy
    tmp_leaf.update(values)

  return out

def get_friendly_name_for_attr(cls, attr_name):
  field = cls._meta.get_field(attr_name)
  return field.related_model().__class__._meta.verbose_name_plural
