# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20151021_0207'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityAreaScan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('scanner', models.ForeignKey(blank=True, to='main.Scanner', null=True)),
                ('tag', models.ForeignKey(to='main.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='rccarscan',
            unique_together=set([('timestamp', 'tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='activityareascan',
            unique_together=set([('timestamp', 'tag')]),
        ),
    ]
