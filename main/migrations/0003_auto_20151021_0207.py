# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20151020_2305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rccarscan',
            name='scanner',
            field=models.ForeignKey(blank=True, to='main.Scanner', null=True),
        ),
    ]
