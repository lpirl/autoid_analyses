from django.shortcuts import render

from main.utils import getattrs, HierarchicalOrderedDict

def index(request):
  return render(request, 'index.html', {})

def related_attr_popularity(request, cls, attr_name):
  # TODO: unify with related_attrs_popularity

  attrs_popularity = cls.get_related_attrs_popularity((attr_name,))
  attrs_popularity = HierarchicalOrderedDict(
    sorted(
      attrs_popularity.iteritems(),
      key=lambda t: t[1]["count"],
      reverse=True
    )
  )

  attr_cls = cls._meta.get_field(attr_name).related_model().__class__
  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_object_name": attr_cls._meta.verbose_name_plural,
    "attrs_popularity": attrs_popularity,
  }
  return render(request, 'attr_popularity.html', context)

def related_attrs_popularity(request, cls, attr_names):
  # TODO: unify with related_attr_popularity

  assert len(attr_names) == 2, "View supports only 2 attribute names."

  attrs_popularity = cls.get_related_attrs_popularity(attr_names)
  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": attr_names,
    "attrs_popularity": attrs_popularity,
  }
  return render(request, 'attrs_popularity.html', context)
