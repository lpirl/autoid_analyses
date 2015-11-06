from uuid import uuid4
from datetime import datetime, timedelta
from random import choice, uniform, gauss

from django.core.management.base import BaseCommand, CommandError

from main import models

class Command(BaseCommand):
  """
  A management command to generate CSV data.
  That data can be stored in a file.
  With that file, in turn, a test database can be populated, as well can
  the import feature be tested.
  """

  help = 'Prints a random CSV of scans.'

  @classmethod
  def get_random_generators(cls):
    """
    Returns a dictionary mapping string names of the available random
    generators to their corresponding class method.
    """
    return {
      "uniform": cls._uniform_random,
      "gauss": cls._gauss_like_random,
    }

  def add_arguments(self, parser):
    """
    Called by Django to enable the Command to add command line arguments.
    """

    random_generator_names = self.get_random_generators().keys()

    parser.add_argument('--scans', type=int, default=100,
        help="number of random scans to generate  (default: 100)")

    parser.add_argument('--tags', type=int, default=1,
        help="number of random tags to generate (default: 1)")
    parser.add_argument('--tags-dist', default="uniform",
        choices=random_generator_names,
        help="distribution to use to pick random tags (default: uniform)")

    parser.add_argument('--scanners', type=int, default=0,
        help="number of random scanners to generate (default: 0)")
    parser.add_argument('--scanners-dist', default="uniform",
        choices=random_generator_names,
        help="distribution to use to pick random scanners (default: uniform)")

    parser.add_argument('--hours', type=int, default=1,
        help="number of hours to generate the random scans within (default: 1)")
    parser.add_argument('--hours-dist', default="uniform",
        choices=random_generator_names,
        help="distribution to use to pick random hours (default: uniform)")

  @classmethod
  def _gauss_like_random(cls, lowest, highest):
    """
    Returns a Gauss-like distributed random float within
    [``lowest``, ``highest``] (inclusively).
    """
    random_multiplier = gauss(3, 1)/6
    range_size = highest - lowest
    unlimited = lowest + range_size * random_multiplier
    limited = min(highest, max(lowest, unlimited))
    return limited

  @classmethod
  def _uniform_random(cls, lowest, highest):
    """
    Retruns a uniformly distributed random float within
    [``lowest``, ``highest``] (inclusively).
    """
    return uniform(lowest, highest)

  @classmethod
  def _rand_with_dist(cls, lowest, highest, random_generator_name):
    """
    Returns a random float using the random number generator specified in
    ``random_generator_name`` within [``lowest``, ``highest``] (inclusively).
    """
    random_generators = cls.get_random_generators()
    random_generator = random_generators[random_generator_name]
    return random_generator(lowest, highest)

  @classmethod
  def _randint_with_dist(cls, lowest, highest, random_generator_name):
    """
    Returns a random int using the random number generator specified in
    ``random_generator_name`` within [``lowest``, ``highest``] (inclusively).
    """
    random = cls._rand_with_dist(lowest, highest, random_generator_name)
    return int(round(random))

  @classmethod
  def _choice_with_dist(cls, items, random_generator_name):
    """
    Choses a random element from ``items`` using the random number
    generator specified in ``random_generator_name``.
    """
    lowest = 0
    highest = len(items)-1
    index = cls._randint_with_dist(lowest, highest, random_generator_name)
    return items[index]

  @staticmethod
  def get_random_components(component_cls, size):
    """
    Returns ``size`` new, unsaved objects of the specified
    ``component_cls``, each with a random PK.
    """
    return [component_cls(pk=str(uuid4())) for _ in range(size)]

  def handle(self, *args, **options):
    """
    Called by Django when the command is invoked.
    This is where the main work is done.
    """

    # plausibility checks for the specified options
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

    # shortcuts
    hours_distribution = options["hours_dist"]
    tags_distribution = options["tags_dist"]
    scanners_distribution = options["scanners_dist"]

    now = datetime.now()
    seconds = options['hours'] * 60 * 60
    self.stdout.write("timestamp,tag,scanner")

    # within this loop, the random scans are generated and printed
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
