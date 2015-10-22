from django.shortcuts import render

from main.models import RCCarScan

def index(request):
  return render(request, 'index.html', {})

def tag_popularity(request, scan_cls):
  scans = scan_cls.objects.select_related('tag').all()
  tags = [s.tag for s in scans]

  tags_with_scancount = []
  for tag in set(tags):
    tags_with_scancount.append((tag, tags.count(tag)))
  tags_with_scancount = sorted(tags_with_scancount, key=lambda t: t[1],
                              reverse=True)

  context = {
    "name": scan_cls._meta.verbose_name_plural,
    "tags_with_scancount": tags_with_scancount,
  }
  return render(request, 'tag_popularity.html', context)
