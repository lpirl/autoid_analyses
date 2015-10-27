from uuid import uuid4
from datetime import datetime, timedelta
from random import choice, uniform, gauss

from django.core.management.base import BaseCommand, CommandError

from main import models

class Command(BaseCommand):
  help = 'Prints a random CSV of scans.'

  @classmethod
  def get_random_generators(cls):
    return {
      "uniform": cls._uniform_random,
      "gauss": cls._gauss_like_random,
    }

  def add_arguments(self, parser):

    random_generator_names = self.get_random_generators().keys()

    parser.add_argument('--scans', type=int, default=100,
        help="number of random scans to generate  (default 100)")

    parser.add_argument('--tags', type=int, default=1,
        help="number of random tags to generate (default 1)")
    parser.add_argument('--tags-dist', default="uniform",
        choices=random_generator_names,
        help="distribution to use to pick random tags (default: uniform)")

    parser.add_argument('--scanners', type=int, default=0,
        help="number of random scanners to generate (default 0)")
    parser.add_argument('--scanners-dist', default="uniform",
        choices=random_generator_names,
        help="distribution to use to pick random scanners (default: uniform)")

    parser.add_argument('--hours', type=int, default=1,
        help="number of hours to generate the random scans within (default 1)")
    parser.add_argument('--hours-dist', default="uniform",
        choices=random_generator_names,
        help="distribution to use to pick random hours (default: uniform)")

  @classmethod
  def _gauss_like_random(cls, lowest, highest):
    random_multiplier = gauss(3, 1)/6
    range_size = highest - lowest
    unlimited = lowest + range_size * random_multiplier
    limited = min(highest, max(lowest, unlimited))
    return limited

  @classmethod
  def _uniform_random(cls, lowest, highest):
    return uniform(lowest, highest)

  @classmethod
  def _rand_with_dist(cls, lowest, highest, random_generator_name):
    random_generators = cls.get_random_generators()
    random_generator = random_generators[random_generator_name]
    return random_generator(lowest, highest)

  @classmethod
  def _randint_with_dist(cls, lowest, highest, random_generator_name):
    random = cls._rand_with_dist(lowest, highest, random_generator_name)
    return int(round(random))

  @classmethod
  def _choice_with_dist(cls, items, random_generator_name):
    lowest = 0
    highest = len(items)-1
    index = cls._randint_with_dist(lowest, highest, random_generator_name)
    return items[index]

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

    hours_distribution = options["hours_dist"]
    tags_distribution = options["tags_dist"]
    scanners_distribution = options["scanners_dist"]

    now = datetime.now()
    seconds = options['hours'] * 60 * 60
    self.stdout.write("timestamp,tag,scanner")
    for _ in range(options["scans"]):
      delta_secs = self._rand_with_dist(0, seconds, hours_distribution)
      time = now - timedelta(0, delta_secs)
      tag = self._choice_with_dist(tags, tags_distribution)
      scanner = self._choice_with_dist(scanners, scanners_distribution)
      self.stdout.write("%s,%s,%s" % (
        time.strftime("%Y-%m-%d %H:%M:%S.%f"),
        tag.component_id,
        scanner.component_id if scanner else "",
      ))
