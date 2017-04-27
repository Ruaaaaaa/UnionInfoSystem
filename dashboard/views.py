# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http import StreamingHttpResponse

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from base.decorators import login_required, admin_required

import json

from base import sessions
from participation.api import *
from dashboard.api import *

# Create your views here.


def file_iterator(file_name, chunk_size=512):
	with open(file_name) as f:
		while True:
			c = f.read(chunk_size)
			if c:
				yield c
			else:
				break
def purifyActivity(cursedactivity):
	purified = {}
	for x in cursedactivity.keys():
		purified[x] = cursedactivity[x]
	purified['signin_restrict'] = (False if purified['signin_restrict'] == u'false' else True) if purified.has_key('signin_restrict') else None
	purified['need_checkin'] = (False if purified['need_checkin'] == u'false' else True) if purified.has_key('need_checkin') else None
	purified['signin_max'] = int(purified['signin_max']) if purified.has_key('signin_max') and purified['signin_restrict'] == True else None
	purified['aaid'] = int(purified['aaid']) if purified.has_key('aaid') else None
	purified['begin_at'] = int(purified['begin_at']) if purified.has_key('begin_at') else None
	purified['end_at'] = int(purified['end_at']) if purified.has_key('end_at') else None
	purified['signin_begin_at'] = int(purified['signin_begin_at']) if purified.has_key('signin_begin_at') else None
	purified['signin_end_at'] = int(purified['signin_end_at']) if purified.has_key('signin_end_at') else None
	return purified

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
	print act_list
	return render(request, 'dashboard/activity.html', {'username':username, 'activities':act_list})



@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
@admin_required
def newActivity(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	if request.method == 'GET':
		return render(request, 'dashboard/new_activity.html', {'type': 'new', 'username': username})
	else:
		#$act_attributes = request.POST
		act_attributes = purifyActivity(request.POST)
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
		return render(request, 'dashboard/new_activity.html', {'activity': activity, 'username': username, 'type': 'edit'})
	else:
		act_attributes = purifyActivity(request.POST)
		authority = activityAuthorityCheck(uid, aaid)
		if authority == -1:
			return JsonResponse({'status': 'error', 'msg': '无此活动！'})
		elif authority == 0:
			return JsonResponse({'status': 'error', 'msg': '您无权修改此活动！'})
		editresult = editActivity(uid, act_attributes)
		if create_result['status'] == 0:
			JsonResponse({'status': 'error', 'msg': '修改活动失败！'})
		else: 
			return JsonResponse({'status': 'success', 'msg': '修改活动成功!'})	


# 先不管这个了，弃疗
@require_http_methods(['GET'])
@login_required
@admin_required
def downloadActivity(request, aaid): 
	return JsonResponse({'status': 'success', 'msg': 'download'})



@require_http_methods(['GET'])
@login_required
@admin_required
def users(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	return render(request, 'dashboard/users.html', {'username': username})



@require_http_methods(['GET'])
@login_required
@admin_required
def getUsers(request):
	page = request.GET['page']
	number = request.GET['number']
	page_total = getUserPageCount(number)
	user_list = getUserListByPageAndNumber(page, number)
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
	return render(request, 'dashboard/broadcast.html', {})