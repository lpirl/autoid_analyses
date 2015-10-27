# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20151023_0546'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkstationLoginScan',
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
            name='workstationloginscan',
            unique_together=set([('timestamp', 'tag')]),
        ),
    ]
