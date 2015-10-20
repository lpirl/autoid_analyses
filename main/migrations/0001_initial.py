# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RCCarScan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Scanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255, blank=True)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255, blank=True)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='rccarscan',
            name='scanner',
            field=models.ForeignKey(to='main.Scanner', blank=True),
        ),
        migrations.AddField(
            model_name='rccarscan',
            name='tag',
            field=models.ForeignKey(to='main.Tag'),
        ),
    ]
