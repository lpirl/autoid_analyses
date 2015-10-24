from django.shortcuts import render

from main.utils import getattrs

def index(request):
  return render(request, 'index.html', {})

def related_attr_popularity(request, cls, attr_name):

  objects = cls.objects.select_related(attr_name)
  attr_objects = getattrs(objects, attr_name)

  # todo: use get_related_attrs_popularity

  attr_objects_with_counts = sorted(
    [(o, attr_objects.count(o)) for o in set(attr_objects)],
    key=lambda t: t[1],
    reverse=True
  )

  attr_objects_count = float(len(attr_objects))
  attr_objects_with_percentiles = sorted(
    [(t[0], t[1]/attr_objects_count) for t in attr_objects_with_counts],
    key=lambda t: t[1]
  )

  attr_cls = cls._meta.get_field(attr_name).related_model().__class__
  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_object_name": attr_cls._meta.verbose_name_plural,
    "attr_objects_with_counts": attr_objects_with_counts,
  }
  return render(request, 'attr_popularity.html', context)

def related_attrs_popularity(request, cls, attr_names):

  assert len(attr_names) == 2, "View supports only 2 attribute names."

  attrs_popularity = cls.get_related_attrs_popularity(attr_names)
  context = {
    "cls_name": cls._meta.verbose_name_plural,
    "attr_names": attr_names,
    "attrs_popularity": attrs_popularity,
  }
  return render(request, 'attrs_popularity.html', context)
