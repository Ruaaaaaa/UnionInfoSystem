# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Department(models.Model):
    did = models.IntegerField(primary_key = True)
    name = models.CharField(max_length = 256)



class Subunion(models.Model):
    suid = models.IntegerField(primary_key = True)
    name = models.CharField(max_length = 256)



class User(models.Model):
    uid = models.IntegerField(primary_key = True)
    is_admin = models.BooleanField(default = 0)
    name = models.CharField(max_length = 32)
    sex = models.BooleanField(default = 0)
    wid = models.CharField(max_length = 32, null = True)
    photo = models.CharField(max_length = 256, null = True)
    id_hash = models.CharField(max_length = 256)
    id_partial = models.CharField(max_length = 32)
    mobile = models.CharField(max_length = 11)
    email = models.CharField(max_length = 256)
    registered = models.BooleanField(default = 0)
    username = models.CharField(max_length = 32)
    password = models.CharField(max_length = 32)
    register_at = models.DateTimeField(null = True)
    last_login_at = models.DateTimeField(null = True)
    department = models.ForeignKey(Department, null = True, related_name = 'users')
    subunion = models.ForeignKey(Subunion, null = True, related_name = 'users')



class Activity(models.Model):
    aid = models.IntegerField(primary_key = True)
    aaid = models.IntegerField()
    content = models.CharField(max_length = 10000)
    creator = models.ForeignKey(User, null = True, related_name = 'activities_created')
    title = models.CharField(max_length = 256)
    description = models.CharField(max_length = 2048)
    poster = models.CharField(max_length = 256, null = True)
    signin_begin_at = models.DateTimeField(null = True)
    signin_end_at = models.DateTimeField(null = True)
    begin_at = models.DateTimeField(null = True)
    end_at = models.DateTimeField(null = True)
    signin_count = models.IntegerField(default = 0)
    signin_max = models.IntegerField(null = True)
    checkin_count = models.IntegerField(default = 0)
    need_checkin = models.BooleanField(default = 1)



class Broadcast(models.Model):
    bid = models.IntegerField(primary_key = True)
    title = models.CharField(max_length = 256)
    content =  models.CharField(max_length = 4096)
    sender =  models.ForeignKey(User, null = True , related_name = 'broadcasts')
    send_at = models.DateTimeField(null = True)
    send_notice = models.BooleanField(default = 0)
    send_email = models.BooleanField(default = 0)
    send_sms = models.BooleanField(default = 0)



class Record(models.Model):
    rid = models.IntegerField(primary_key = True)
    user = models.ForeignKey(User, null = True, related_name = 'records')
    activity = models.ForeignKey(Activity, null = True, related_name = 'records')
    signin_at = models.DateTimeField(null = True)
    checked_in = models.BooleanField(default = 0)
    checkin_at = models.DateTimeField(null = True)



class Message(models.Model):
    mid = models.IntegerField(primary_key = True)
    broadcast = models.ForeignKey(Broadcast, null = True, related_name = 'messages')
    sender = models.ForeignKey(User, null = True, related_name = 'messages_sended')
    receiver = models.ForeignKey(User, null = True, related_name = 'messages_received')
    send_at = models.DateTimeField(null = True)
    received = models.BooleanField(default = 0)
    receive_at = models.DateTimeField(null = True)
