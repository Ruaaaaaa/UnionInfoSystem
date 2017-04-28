# -*- coding: utf-8 -*-
"""
Database interface for views.py
"""
from __future__ import unicode_literals
from base.models import *
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import model_to_dict
import datetime
import hashlib

def getUidByUsername(username):
    try:
        user = User.objects.get(username = username)
    except ObjectDoesNotExist:
        print u"没有这个用户名"
        return -1
    return user.uid

def getUsernameByUid(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"没有这个用户名"
        return -1
    return user.username

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
    user.username = username
    user.password = pwd
    user.mobile = mobile
    user.email = email
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
    rec.checkin_at = (datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds()
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
    #print datetime.datetime.timetuple()
    try:
        user.records.get(aaid=aaid)
    except ObjectDoesNotExist:
        rec = Record(
            aid = act.aid,
            aaid = act.aaid,
            uid = user.uid,
            user = user,
            activity = act,
            signin_at = (datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds()
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

def getActivitiesByUidSimple(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"无用户"
        return 0
    actlist = []
    for act in user.activities_created.all():
        actlist.append(model_to_dict(act, exclude = ['content']))
    return actlist

def getActivitiesInvolvedByUid(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"无用户"
        return 0
    try:
        records = user.records.all()
    except ObjectDoesNotExist:
        print u"没有活动"
        return []
    actlist = []
    for rec in records:
        actlist.append(model_to_dict(rec.activity, exclude = ['content']))
    return actlist

def createNewActivity(uid, act_attributes):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        return {'status' : 'error', 'msg' : '无用户', 'aaid' : -1}
    if not user.is_admin:
        return {'status': 'error', 'msg': '不是管理员', 'aaid' : -1}
    m = hashlib.md5()
    m.update(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    aaid_md = m.hexdigest()
    aaid_md = aaid_md[0:10]
    act = Activity(
        aaid = aaid_md,
        creator = user,
        title = act_attributes['title'],
        description = act_attributes['description'],
        content = act_attributes['content'],
        signin_begin_at = act_attributes['signin_begin_at'],
        signin_end_at = act_attributes['signin_end_at'],
        begin_at = act_attributes['begin_at'],
        end_at = act_attributes['end_at'],
        signin_max = act_attributes['signin_max'],
        need_checkin = act_attributes['need_checkin']
    )
    act.save()
    return {'status' : 'success', 'msg' : '创建成功', 'aaid' : act.aaid}

def activityAuthorityCheck(uid, aaid):
    try:
        act = Activity.objects.get(aaid = aaid)
    except ObjectDoesNotExist:
        return -1
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        return -1
    return act.creator.uid == uid

def getUserPageCount(number):
    count = User.objects.all().count()
    print number, type(number)
    return ((count-1) / number ) +1

def filterUsers(departments, activities, checked_in):
    userlist=[]

    for i in range(1,100000000):
        try:
            user = User.objects.get(uid = i)
        except ObjectDoesNotExist:
            break

        if len(departments) > 0:
            flag = 0
            for i in range(0, len(departments)):
                if departments[i] == user['department']:
                    flag = 1
                    break
            if not flag: continue 
        if len(sub_unions) > 0:
            flag = 0
            for i in range(0, len(sub_unions)):
                if sub_unions[i] == user['sub_union']:
                    flag = 1
                    break
            if not flag: continue 
        if len(activities) > 0:
            flag = 0
            for i in range(0, len(activities)):
                try:
                    record = user.records.get(aid = activities[i])
                except ObjectDoesNotExist:
                    continue 
                if record['checked_in'] == False:
                    continue
                flag = 1
                break
            if not flag: continue   

        userlist.append(model_to_dict(user))
    return userlist

def getBroadcastsSendedByUid(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"无用户"
        return 0
    if not user.is_admin:
        print u"不是管理员"
        return 0
    broadcastlist = []
    for broadcast in user.broadcasts.all():
        broadcastlist.append(model_to_dict(broadcast))
    return broadcastlist

def getBroadcastsReceivedByUid(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"无用户"
        return 0
    try:
        messages = user.messages_received.all()
    except ObjectDoesNotExist:
        print u"没有消息"
        return []
    broadcastlist = []
    for message in massages:
        broadcastlist.append(model_to_dict(message.broadcast))
    return broadcastlist

def doEditActivity(uid,act_attributes):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print 'no user'
        return 0
    try:
        print act_attributes['aaid']
        act = Activity.objects.get(aaid = act_attributes['aaid'])
    except ObjectDoesNotExist:
        print 'no activity'
        return 0
    if user != act.creator:
        print 'not match'
        return 0
    act.title = act_attributes['title']
    act.description = act_attributes['description']
    act.content = act_attributes['content']
    act.signin_begin_at = act_attributes['signin_begin_at']
    act.signin_end_at = act_attributes['signin_end_at']
    act.begin_at = act_attributes['begin_at']
    act.end_at = act_attributes['end_at']
    act.signin_max = act_attributes['signin_max']
    act.need_checkin = act_attributes['need_checkin']
    act.save()
    return 1
