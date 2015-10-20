from django.db import models

class AbstractRFIDComponent(models.Model):
  """
  Represents a physical component involved in RFID scanning
  (i.e. scanner or tag).
  """

  class Meta:
    abstract = True

  component_id = models.CharField(max_length=64, primary_key=True,
      help_text="The ID that is used in imported data.")
  friendly_name = models.CharField(max_length=64, blank=True,
      help_text="Might be used to ease readability for humans.")
  comments = models.TextField(blank=True)

class Tag(AbstractRFIDComponent):
  """
  Represents a physical RFID tag.
  """
  pass

class Scanner(AbstractRFIDComponent):
  """
  Represents a physical RFID scanner.
  """
  pass

class AbstractScan(models.Model):
  """
  Represents a scan, i.e. a tag at a possibly known scanner.
  """

  class Meta:
    abstract = True

  timestamp = models.DateTimeField(db_index=True)
  tag = models.ForeignKey("Tag")
  scanner = models.ForeignKey("Scanner", blank=True)

class RCCarScan(AbstractScan):
  pass
