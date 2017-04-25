# -*- coding: utf-8 -*-
"""
Database interface for views.py
"""
from __future__ import unicode_literals
from models import *
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

def getUidByName(name):
    return 1
    try:
        user = User.objects.get(name = name)
    except ObjectDoesNotExist:
        print u"没有这个用户名"
        return
    return user.uid

def verifyPassword(uid, pwd):
    if uid == 1 and pwd == '123456':
        return 1
    else:
        return 0
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"没有这个用户"
        return
    user.password = pwd
    user.save()

def getIdentityByUid(uid):
    return 0
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"没有这个用户"
        return
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

