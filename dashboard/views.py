# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from base.decorators import login_required, admin_required

import json
import os
import xlrd
import xlwt

from InfoSystem.shared import dashboard_tabs
from base import sessions
from participation.api import *
from dashboard.api import *
# Create your views here.


def file_iterator(file_name, chunk_size=8192):
	with open(file_name, "rb") as f:
		while True:
			c = f.read(chunk_size)
			if c:
				yield c
			else:
				break


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def login(request):

	# 如果已经管理员session，转到activity
	# 如果已经普通用户session，转到404
	# 否则，再渲染登录界面

	if request.method == 'GET':
		user = sessions.getUser(request)
		print user
		print getIdentityByUid(user[0])
		if user[0] == None or user[1] == None:
			return render(request, 'dashboard/login.html', {})
		else:
			if user[1] == 1:
				raise Http404
			else:
				return HttpResponseRedirect('/admin/activity')
	else:
		if not request.POST.has_key('username') or not request.POST.has_key('pwd'):
			return JsonResponse({'status': 'error', 'msg': '请输入用户名和密码。'})
		username = request.POST['username'] 
		pwd = request.POST['pwd']

		uid = getUidByUsername(username)
		if uid == -1: # no such username 
			return JsonResponse({'status': 'error', 'msg': '没有这个账号!'})
		if verifyPassword(uid, pwd) == False:
			return JsonResponse({'status': 'error', 'msg': '用户名或密码错误!'})
		identity = getIdentityByUid(uid)
		if sessions.login(request, uid, identity) == False:
			return JsonResponse({'status': 'error', 'msg': '登录失败!'})
		return JsonResponse({'status': 'success', 'msg': '登陆成功!'})
		


@require_http_methods(['GET'])
@login_required
@admin_required
def activity(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	act_list = getActivitiesByUidSimple(uid)
	return render(request, 'dashboard/activity.html', {'tab': dashboard_tabs['activity'], 'username': username, 'activities': act_list})



@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
@admin_required
def newActivity(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	if request.method == 'GET':
		return render(request, 'dashboard/new_activity.html', {'tab': dashboard_tabs['activity'], 'type': 'new', 'username': username})
	else:
		act_attributes = json.loads(request.POST['data'])
		imagefile = request.FILES['poster']
		act_attributes['image'] = ContentFile(imagefile.read())
		create_result = createNewActivity(uid, act_attributes)
		if create_result['status'] == "error":
			JsonResponse({'status': 'error', 'msg': create_result['msg']})
		else:
			return JsonResponse({'status': 'success', 'msg': '创建活动成功!', 'data': {'aaid': create_result['aaid']} })



@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
@admin_required
def editActivity(request, aaid):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	activity = getActivityByAaid(aaid)	
	if activity == -1: 
		raise Http404
	if request.method == 'GET':
		return render(request, 'dashboard/new_activity.html', {'tab': dashboard_tabs['activity'], 'activity': activity, 'username': username, 'type': 'edit'})
	else:
		act_attributes = json.loads(request.POST['data'])
		act_attributes ['aaid'] = aaid
		authority = activityAuthorityCheck(uid, aaid)
		if authority == -1:
			return JsonResponse({'status': 'error', 'msg': '无此活动！'})
		elif authority == 0:
			return JsonResponse({'status': 'error', 'msg': '您无权修改此活动！'})

		imagefile = request.FILES['poster']
		act_attributes['image'] = ContentFile(imagefile.read())
		editresult = doEditActivity(uid, act_attributes)
		if editresult == 0:
			return JsonResponse({'status': 'error', 'msg': '修改活动失败！'})
		else: 
			return JsonResponse({'status': 'success', 'msg': '修改活动成功!'})	



@require_http_methods(['GET'])
@csrf_exempt
@login_required
@admin_required
def deleteActivity(request, aaid):
	uid = sessions.getUser(request)[0] 
	authority = activityAuthorityCheck(uid, aaid)
	if authority == -1:
		return JsonResponse({'status': 'error', 'msg': '无此活动！'})
	elif authority == 0:
		return JsonResponse({'status': 'error', 'msg': '您无权删除此活动！'})
	deleteresult = doDeleteActivity(uid, aaid)
	if deleteresult == 0:
		return JsonResponse({'status': 'error', 'msg': '删除活动失败！'})
	else:
		return JsonResponse({'status': 'success', 'msg': '删除活动成功!'})	


# 先不管这个了，弃疗
@require_http_methods(['GET'])
@login_required
@admin_required
def downloadActivity(request, aaid): 

	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	if activityAuthorityCheck(uid, aaid) != 1:
		return JsonResponse({'status': 'error', 'msg': '无权下载此活动信息！'})

	#excel part
	dirpath = r"dashboard/files/%s"%aaid
	print dirpath
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)
	xlpath = dirpath+"/userinfo.xls"
	style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
	    num_format_str='#,##0.00')
	style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

	wb = xlwt.Workbook()
	ws = wb.add_sheet('A Test Sheet')

	ws.write(0, 0, 1234.56, style0)
	ws.write(1, 0, datetime.datetime.now(), style1)
	ws.write(2, 0, 1)
	ws.write(2, 1, 1)
	ws.write(2, 2, xlwt.Formula("A3+B3"))
	wb.save(xlpath)

	#txt part

	#packagepart


	response = StreamingHttpResponse(file_iterator(xlpath))
	response['Content-Disposition'] = 'attachment;filename="userinfo_%s.xls"'%aaid
	return response

@require_http_methods(['GET'])
@login_required
@admin_required
def users(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	return render(request, 'dashboard/users.html', {'tab': dashboard_tabs['users'], 'username': username})




@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def getUsers(request):
	dic = json.loads(request.body)
	try:
		page = dic['page']
		number = dic['number']
		departments = dic['departments']
		sub_unions = dic['sub_unions']
		activities = dic['activities']
		checked_in = dic['checked_in']
	except Exception,e:  
		return JsonResponse({'status': 'error', 'msg': e})
	#page_total = getUserPageCount(number)
	user_list, page_total = getUserListByFilter(page, number, departments, sub_unions, activities, checked_in)
	return JsonResponse({'status': 'success', 'msg': 'users', 'data':{'page_total':page_total, 'user_list':user_list}})


#先不管了，弃疗
@require_http_methods(['GET'])
@login_required
@admin_required
def downloadUsers(request):	
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	file_name = "dashboard/files/1.txt"
	response = StreamingHttpResponse(file_iterator(file_name))
	response['Content-Type'] = 'application/octet-stream'
	response['Content-Disposition'] = 'attachment;filename="userlist.txt"'
	return response

	#return JsonResponse({'status': 'success', 'msg': 'download'})


# 先不管这个了，弃疗
@require_http_methods(['GET'])
@login_required
@admin_required
def broadcast(request):
	return render(request, 'dashboard/broadcast.html', {'tab': dashboard_tabs['broadcast']})

@require_http_methods(['GET'])
@login_required
@admin_required
def getActivities(request):
	return JsonResponse({'status':'success', 'msg': '获取活动列表成功！', 'data': {'activities': getActivityListSimple()}})


@require_http_methods(['GET'])
@login_required
@admin_required
def getSubUnions(request):
	return JsonResponse({'status':'success', 'msg': '获取分工会列表成功！', 'data': {'subunions': getSubUnionListSimple()}})


@require_http_methods(['GET'])
@login_required
@admin_required
def getDepartments(request):
	return JsonResponse({'status':'success', 'msg': '获取部门列表成功！', 'data': {'departments': getDepartmentListSimple()}})