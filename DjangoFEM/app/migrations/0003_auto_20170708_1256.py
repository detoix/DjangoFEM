# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-08 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20170708_1134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='element',
            name='node_end',
        ),
        migrations.AddField(
            model_name='element',
            name='node_end',
            field=models.ManyToManyField(related_name='node_end', to='app.Node'),
        ),
        migrations.RemoveField(
            model_name='element',
            name='node_start',
        ),
        migrations.AddField(
            model_name='element',
            name='node_start',
            field=models.ManyToManyField(related_name='node_start', to='app.Node'),
        ),
    ]
