# -*- coding: utf-8 -*-
"""
Database interface for views.py
"""
from __future__ import unicode_literals
from base.models import *
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import model_to_dict
import datetime

def getUidByUsername(username):
    try:
        user = User.objects.get(username = username)
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
    return user.password == pwd

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
        user = User(id_hash = idnumber)
        user.save()
        print u"没有这个身份证号"
        return 0
    if user.registered :
        return 2
    if realname == user.name :
        return 1
    else:
        return 0

def registerAccount(idnumber, username, pwd, mobile, email):
    try:
        user = User.objects.get(id_hash = idnumber)
    except ObjectDoesNotExist:
        #user = User(id_hash = idnumber)
        #user.save() 
        print u"没有这个身份证号"
        return 0
    #print 'id',idnumber,'username',username
    user.username = username
    user.password = pwd
    user.mobile = mobile
    user.email = email
    user.registered = true
    user.register_at = datetime.datetime.now()
    user.save()
    return 1

def getActivityByAaid(aaid):
    try:
        acti = Activity.objects.get(aaid = aaid)
    except ObjectDoesNotExist:
        print u"无此活动"
        return -1
    #user = User.objects.get(id_hash=idnumber)
    return model_to_dict(acti)

def userCheckIn(uid, aaid):
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
        print u"未报名"
        return 0
    if rec.check_in:
        print u"签到过了"
        return 2
    rec.check_in = 1
    rec.checkin_at = datetime.datetime.now()
    rec.save()
    print "签到成功"
    return 1

def userSignIn(uid, aaid):
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
        user.records.get(aaid=aaid)
    except ObjectDoesNotExist:
        rec = Record(
            aid = act.aid,
            aaid = act.aaid,
            uid = user.uid,
            user = user,
            activity = act,
            signin_at = datetime.datetime.now()
        )
        rec.save()
        return 1
    print u"报名过了"
    return 2

def registeredUsername(username):
    try:
        user = User.objects.get(username = username)
    except ObjectDoesNotExist:
        return 0
    return 1
