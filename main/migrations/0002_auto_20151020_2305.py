# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scanner',
            name='id',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='name',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='id',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='name',
        ),
        migrations.AddField(
            model_name='scanner',
            name='friendly_name',
            field=models.CharField(help_text=b'Might be used to ease readability for humans.', max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='friendly_name',
            field=models.CharField(help_text=b'Might be used to ease readability for humans.', max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='component_id',
            field=models.CharField(help_text=b'The ID that is used in imported data.', max_length=64, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='component_id',
            field=models.CharField(help_text=b'The ID that is used in imported data.', max_length=64, serialize=False, primary_key=True),
        ),
    ]
