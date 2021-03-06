# -*- coding: utf-8 -*-
"""
Database interface for views.py
"""
from __future__ import unicode_literals
from base.models import *
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import model_to_dict
import datetime
import time
import hashlib
import os

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
        print u"没有这个身份证号"
        return 0
    user.registered = 1
    user.username = username
    user.password = pwd
    user.mobile = mobile
    user.email = email
    user.register_at = (datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds()
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
    print 'name?',act_attributes['filename']
    (pre,suf) = os.path.splitext(act_attributes['filename'])
    act.poster.save(aaid_md+'.'+suf,act_attributes['image'],0)
    act.save()
    return {'status' : 'success', 'msg' : '创建成功', 'aaid' : act.aaid}

def createBroadcast(dic):
    try:
        user = User.objects.get(uid = dic['uid'])
    except ObjectDoesNotExist:
        return {'status' : 'error', 'msg' : '用户不存在。'}
    if not user.is_admin:
        return {'status': 'error', 'msg': '该用户没有发布消息的权利。'}
    m = hashlib.md5()
    m.update(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    bid_md = m.hexdigest()
    bid_md = bid_md[0:10]
    deps = Department.objects.filter(did__in = dic['departments'])
    subs = Subunion.objects.filter(suid__in = dic['sub_unions'])
    tags_list = []
    for dep in deps:
        tags_list += [dep.name]
    for sub in subs:
        tags_list += [sub.name]
    if dic['checked_in'] :
        tags_list += ['已签到']
    st = ","
    tags = st.join(tags_list)
    print tags
    print dic
    broadcast = Broadcast(
        bbid = bid_md,
        title = dic['title'],
        content = dic['content'],
        sender = user,
        sender_name = dic['sender'],
        send_at = (datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds(),
        send_notice = dic['send_notice'],
        send_email = dic['send_email'],
        send_sms = dic['send_sms'],
        tags = tags
    )
    broadcast.save()
    print broadcast
    return {'status' : 'success', 'msg' : '创建成功'}

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


def getUserListByFilter(page, number, departments, sub_unions, activities, check_in):
    userlist=[]
    users = User.objects.all().exclude(is_admin = 1)
    if len(departments) > 0:
        deps = Department.objects.filter(did__in = departments)
        users = User.objects.filter(department__in = deps)
    if len(sub_unions) > 0:
        subs = Subunion.objects.filter(suid__in = sub_unions)
        users = users.filter(subunion__in = subs)
    if len(activities) > 0:
        acts = Activity.objects.filter(aid__in = activities)
        recs = Record.objects.filter(activity__in = acts)
        if check_in :
            recs = recs.fillter(checked_in = 1)
        uids = []
        for rec in recs:
            uids.append(rec.user.uid)
        users = users.filter(uid__in = uids)
    count = 0
    for user in users:
        count = count + 1
        if (count >= number*(page-1)+1 and count <= number*page):
            dict = model_to_dict(user)
            dict['sex_text'] = u'男' if user.sex else u'女'
            dict['department_text'] = user.department.name
            dict['sub_union_text'] = user.subunion.name
            dict['photo'] = ''
            userlist.append(dict)
    return (userlist, (count-1)/number+1)


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
    act.poster.save(act.aaid+'.jpg',act_attributes['image'],0)
    act.save()
    return 1

def updateUserLoginTime(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"无此用户"
        return 0
    user.last_login_at = (datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds()
    user.save()

def getUserInformationListByActivity(aaid):
    list = []
    try:
        activity = Activity.objects.get(aaid = aaid)
    except ObjectDoesNotExist:
        print u"无此活动"
        return []
    records = activity.records.all()
    for record in records :
        user = record.user
        dic = model_to_dict(user)
        dic['rid'] = record.rid
        dic['signin_at'] = record.signin_at
        dic['checked_in'] = record.checked_in
        dic['checkin_at'] = record.checkin_at
        list.append(dic)
    return list

def getBroadcastByPage(page, number):
    old_news_list=[]
    broadcasts = Broadcast.objects.all().order_by("-send_at")
    count = 0
    for broadcast in broadcasts:
        count = count + 1
        if (count >= number * (page - 1) + 1 and count <= number * page):
            dict = model_to_dict(broadcast)
            if dict['tags'] == "" :
                dict['tags'] = ['所有人']
            else:
                dict['tags'] = dict['tags'].split(',')
            dict['send_at'] = time.strftime('%Y/%m/%d  %H:%M:%S',time.localtime(dict['send_at']))
            old_news_list.append(dict)
    return (old_news_list, (count - 1) / number + 1)