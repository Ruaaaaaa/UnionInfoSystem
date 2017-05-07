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
import xlrd


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
        print u"没有身份证号"
        try:
            user1 = User.objects.get(wid_hash = idnumber)
        except ObjectDoesNotExist:
            print u"没有这个工号"
            return 0
        user = user1
    if user.registered :
        return (2,getUserByUid(user.uid))
    if realname == user.name :
        return (1,getUserByUid(user.uid))
    else:
        return (0,-1)

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
            dict['sub_union_text'] = user.department.subunion.name
            dict['formation_text'] = user.formation.name
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
    (pre,suf) = os.path.splitext(act_attributes['filename'])
    act.poster.save(act_attributes['aaid']+'.'+suf,act_attributes['image'],0)
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


def getUserByUid(uid):
    try:
        user = User.objects.get(uid = uid)
    except ObjectDoesNotExist:
        print u"无用户"
        return -1
    dict = model_to_dict(user)
    dict['sex_text'] = u'男' if user.sex else u'女'
    dict['department_text'] = user.department.name
    dict['sub_union_text'] = user.department.subunion.name
    dict['formation_text'] = user.formation.name
    return dict


def getRecordByUidAndAaid(uid, aaid):
    try:
        record = Record.objects.get(uid = uid, aaid = aaid)
    except ObjectDoesNotExist:
        print u"未报名"
        return -1
    return model_to_dict(record)

def getDepartmentByDid(did):
    try:
        department = Department.objects.get(did = did)
    except ObjectDoesNotExist:
        print u"无单位"
        return -1
    return model_to_dict(department)

def getSubunionBySuid(suid):
    try:
        sub = Subunion.objects.get(suid = suid)
    except ObjectDoesNotExist:
        print u"无工会"
        return -1
    return model_to_dict(sub)

def getFormationByFid(fid):
    try:
        formation = Formation.objects.get(fid = fid)
    except ObjectDoesNotExist:
        print u"无制编"
        return -1
    return model_to_dict(formation)




'''

try:
    shibian = Formation.objects.get(name = u'正式事业编制')
except ObjectDoesNotExist:
    shibian = Formation(
        name = u'正式事业编制',
        is_career = 1
    )
    shibian.save()
shibian = Formation.objects.get(name=u'正式事业编制')
data = xlrd.open_workbook('/home/lilingxin/UnionInfoSystem/A.xls')
table = data.sheets()[0]
ncols = table.ncols
nrows = table.nrows
for i in range(1,nrows):
    ddid = table.cell(i, 0).value
    dep_name = table.cell(i, 1).value
    try:
        department = Department.objects.get(name = dep_name)
    except ObjectDoesNotExist:
        try:
            subunion = Subunion.objects.get(name = dep_name)
        except ObjectDoesNotExist:
            subunion = Subunion(
                name = dep_name
            )
            subunion.save()
        subunion = Subunion.objects.get(name=dep_name)
        department = Department(
            name = dep_name,
            ddid = ddid,
            subunion = subunion
        )
        department.save()
    department = Department.objects.get(name=dep_name)
    forma = table.cell(i, 5).value


    wid = table.cell(i, 2).value
    wid = wid.encode('utf-8')
    id = table.cell(i, 3).value
    id = id.encode('utf-8')
    name = table.cell(i,4).value


    m = hashlib.md5()
    m.update(id)
    idhash = m.hexdigest()
    m.update(wid)
    widhash = m.hexdigest()
    try:
        user = User.objects.get(id_hash = idhash)
    except ObjectDoesNotExist:
        user = User(
            name = name,
            id_hash = idhash,
            id_partial = id[0:3]+id[14:18],
            wid = wid,
            wid_hash = widhash,
            department = department,
            formation = shibian
        )
        user.save()
    #print str(i+1)+'/'+str(nrows)


try:
    hetong = Formation.objects.get(name = u'合同制')
except ObjectDoesNotExist:
    hetong = Formation(
        name = u'合同制',
        is_career = 0
    )
    hetong.save()
try:
    laowu = Formation.objects.get(name = u'劳务派遣')
except ObjectDoesNotExist:
    laowu = Formation(
        name = u'劳务派遣',
        is_career = 0
    )
    laowu.save()

data = xlrd.open_workbook('/home/lilingxin/UnionInfoSystem/B.xlsx')
table = data.sheets()[0]
ncols = table.ncols
nrows = table.nrows

for i in range(1,nrows):
    dep_name = table.cell(i, 3).value
    subunion_name = table.cell(i, 4).value
    try:
        subunion = Subunion.objects.get(name=subunion_name)
    except ObjectDoesNotExist:
        subunion = Subunion(
            name=subunion_name
        )
        subunion.save()
    subunion = Subunion.objects.get(name=subunion_name)
    try:
        department = Department.objects.get(name = dep_name)
    except ObjectDoesNotExist:
        department = Department(
            name = dep_name,
            subunion = subunion
        )
        department.save()
    department = Department.objects.get(name=dep_name)
    forma = table.cell(i, 5).value
    #print type(forma),forma
    try:
        formation = Formation.objects.get(name = forma)
    except ObjectDoesNotExist:
        formation = Formation(
            name = forma,
            is_career = 0
        )
        formation.save()
    formation = Formation.objects.get(name=forma)
    wid = table.cell(i, 2).value
    #print type(wid),wid
    wid = str(int(wid))
    #wid = wid.encode('utf-8')
    name = table.cell(i,0).value
    sex = 1 if table.cell(i,1).value == u'男' else 0
    m = hashlib.md5()
    m.update(wid)
    widhash = m.hexdigest()
    #print type(name),name,type(sex),sex,type(wid),wid,type(widhash),widhash
    try:
        user = User.objects.get(wid_hash = widhash)
    except ObjectDoesNotExist:
        user = User(
            name = name,
            sex = sex,
            wid = wid,
            wid_hash = widhash,
            department = department,
            formation = formation
        )
        user.save()
    #print str(i+1)+'/'+str(nrows)
'''
