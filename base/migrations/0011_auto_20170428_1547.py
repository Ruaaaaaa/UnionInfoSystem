# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 15:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20170427_2329'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo_path',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(null=True, upload_to='photos'),
        ),
    ]
