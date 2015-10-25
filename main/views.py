from django.shortcuts import render

from main.utils import getattrs, HierarchicalOrderedDict

def index(request):
  return render(request, 'index.html', {})

def related_attrs_popularity(request, cls, attr_names):

  get_field = cls._meta.get_field
  attr_verbose_names = [
    get_field(n).related_model().__class__._meta.verbose_name_plural
    for n in attr_names
  ]

  attrs_popularity = cls.get_related_attrs_popularity(attr_names)

  attrs_count = len(attr_names)
  if attrs_count == 1:
    # TODO: find a generic way to sort a hierarchal dict
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
