# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-20 14:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('aid', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=2048)),
                ('poster', models.CharField(max_length=256, null=True)),
                ('signin_begin_at', models.DateTimeField(null=True)),
                ('signin_end_at', models.DateTimeField(null=True)),
                ('begin_at', models.DateTimeField(null=True)),
                ('end_at', models.DateTimeField(null=True)),
                ('signin_count', models.IntegerField(default=0)),
                ('signin_max', models.IntegerField(default=0, null=True)),
                ('checkin_count', models.IntegerField(default=0)),
                ('need_checkin', models.BooleanField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Broadcast',
            fields=[
                ('bid', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('content', models.CharField(max_length=4096)),
                ('send_at', models.DateTimeField(null=True)),
                ('send_notice', models.BooleanField(default=0)),
                ('send_email', models.BooleanField(default=0)),
                ('send_sms', models.BooleanField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('mid', models.IntegerField(primary_key=True, serialize=False)),
                ('send_at', models.DateTimeField(null=True)),
                ('received', models.BooleanField(default=0)),
                ('receive_at', models.DateTimeField(null=True)),
                ('broadcast', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Broadcast')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('rid', models.IntegerField(primary_key=True, serialize=False)),
                ('signin_at', models.DateTimeField(null=True)),
                ('checked_in', models.BooleanField(default=0)),
                ('checkin_at', models.DateTimeField(null=True)),
                ('activity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('uid', models.IntegerField(primary_key=True, serialize=False)),
                ('is_admin', models.BooleanField(default=0)),
                ('name', models.CharField(max_length=32)),
                ('sex', models.BooleanField(default=0)),
                ('wid', models.CharField(max_length=32, null=True)),
                ('photo', models.CharField(max_length=256, null=True)),
                ('id_hash', models.CharField(max_length=256)),
                ('id_partial', models.CharField(max_length=32)),
                ('mobile', models.CharField(max_length=11)),
                ('email', models.CharField(max_length=256)),
                ('registered', models.BooleanField(default=0)),
                ('username', models.CharField(max_length=32)),
                ('password', models.CharField(max_length=32)),
                ('register_at', models.DateTimeField(null=True)),
                ('last_login_at', models.DateTimeField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='record',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.User'),
        ),
        migrations.AddField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_received', to='base.User'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_sended', to='base.User'),
        ),
        migrations.AddField(
            model_name='broadcast',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.User'),
        ),
        migrations.AddField(
            model_name='activity',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.User'),
        ),
    ]