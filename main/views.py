from django.shortcuts import render

from main.models import RCCarScan

def index(request):
  return render(request, 'index.html', {})

def tag_popularity(request, scan_cls):
  context = {
    "name": scan_cls._meta.verbose_name_plural,
  }
  return render(request, 'tag_popularity.html', context)
