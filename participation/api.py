# -*- coding: utf-8 -*-
"""
Database interface for views.py
"""
from __future__ import unicode_literals
from models import *
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import model_to_dict
import datetime

def getUidByName(name):
    try:
        user = User.objects.get(name = name)
    except ObjectDoesNotExist:
        print u"没有这个用户名"
        return -1
    return user.uid

def verifyPassword(uid, pwd):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"没有这个用户"
        return -1
    user.password = pwd
    user.save()

def getIdentityByUid(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"没有这个用户"
        return -1
    return not user.is_admin

def verificationOfRealId(realname, idnumber):
    try:
        user = User.objects.get(id_hash = idnumber)
    except ObjectDoesNotExist:
        print u"没有这个身份证号"
        return 0
    if user.registered :
        return 2
    if realname == user.name :
        return 1
    else:
        return 0

def registerAccount(idnumber, username, pwd):
    try:
        user = User.objects.get(id_hash = idnumber)
    except ObjectDoesNotExist:
        print u"没有这个身份证号"
        return 0
    user.username = usernanme
    user.password = pwd
    user.save()
    return 1

def getActibityByAaid(aaid):
    try:
        acti = Activity.objects.get(aaid = aaid)
    except ObjectDoesNotExist:
        print u"无此活动"
        return -1
    #user = User.objects.get(id_hash=idnumber)
    return model_to_dict(acti)

def userCheckin(uid, aaid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"无此用户"
        return 0
    try:
        act = Activity.objects.get(aaid = aaid)
    except ObjectDoesNotExist:
        print u"无活动"
        return 0
    try:
        rec = user.records.get(aaid = aaid)
    except ObjectDoesNotExist:
        if rec.check_in:
            print u"签到过了"
            return 2
        rec.check_in = 1
        rec.checkin_at = datetime.datetime.now()
        rec.save()
        print "签到成功"
        return 1
    print u"未报名"
    return 0

