# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-25 19:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20170425_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='content',
            field=models.CharField(default='', max_length=10000),
            preserve_default=False,
        ),
    ]
