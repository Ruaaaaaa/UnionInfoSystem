# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 05:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20170428_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcast',
            name='sender_name',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='broadcast',
            name='tags',
            field=models.CharField(max_length=4096, null=True),
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='bid',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='send_at',
            field=models.CharField(max_length=256, null=True),
        ),
    ]