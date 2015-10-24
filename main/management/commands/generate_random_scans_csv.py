from uuid import uuid4
from datetime import datetime, timedelta
from random import choice, random

from django.core.management.base import BaseCommand, CommandError

from main import models

class Command(BaseCommand):
  help = 'Prints a random CSV of scans.'

  def add_arguments(self, parser):
    parser.add_argument('--scans', type=int, default=100,
        help="number of random scans to generate  (default 100)")
    parser.add_argument('--tags', type=int, default=1,
        help="number of random tags to generate (default 1)")
    parser.add_argument('--scanners', type=int, default=0,
        help="number of random scanners to generate (default 0)")
    parser.add_argument('--hours', type=int, default=1,
        help="number of hours to generate the random scans within (default 1)")
    # todo: add different random distributions via
    #   https://docs.python.org/dev/library/argparse.html#choices
  @staticmethod
  def get_random_components(component_cls, size):
    return [component_cls(pk=str(uuid4())) for _ in range(size)]

  def handle(self, *args, **options):

    if options['scans'] < 1:
      raise CommandError('Number of scans to generate must be at least 1.')
    if options['tags'] < 1:
      raise CommandError('Number of tags to generate must be at least 1.')
    if options['hours'] == 0:
      raise CommandError('Number of hours must be not 0.')

    tags = self.get_random_components(models.Tag, options['tags'])

    if options['scanners'] > 0:
      scanners = self.get_random_components(models.Scanner,
                                            options['scanners'])
    else:
      scanners = [None]

    now = datetime.now()
    seconds = options['hours'] * 60 * 60
    self.stdout.write("timestamp,tag,scanner")
    for _ in range(options["scans"]):
      time = now - timedelta(0, random() * seconds)
      tag = choice(tags)
      scanner = choice(scanners)
      self.stdout.write("%s,%s,%s" % (
        time.strftime("%Y-%m-%d %H:%M:%S.%f"),
        tag.component_id,
        scanner.component_id if scanner else "",
      ))
