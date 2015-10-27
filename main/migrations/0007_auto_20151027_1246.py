# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20151027_1238'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='activityareascan',
            unique_together=set([('timestamp', 'tag', 'scanner')]),
        ),
        migrations.AlterUniqueTogether(
            name='rccarscan',
            unique_together=set([('timestamp', 'tag', 'scanner')]),
        ),
        migrations.AlterUniqueTogether(
            name='videoscan',
            unique_together=set([('timestamp', 'tag', 'scanner')]),
        ),
        migrations.AlterUniqueTogether(
            name='workstationloginscan',
            unique_together=set([('timestamp', 'tag', 'scanner')]),
        ),
    ]
