from django.shortcuts import render

from main.models import RCCarScan

def index(request):
  return render(request, 'index.html', {})

def popularity(request, cls, attr_name):

  objects = cls.objects.select_related(attr_name).all()
  attr_objects = [getattr(o, attr_name) for o in objects]

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
  return render(request, 'popularity.html', context)
