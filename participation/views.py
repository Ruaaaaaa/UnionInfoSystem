# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from base.decorators import login_required, admin_required

from base import sessions
from api import *
import md5

# Create your views here.

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def login(request):
	if sessions.getUser(request)[0] != None:
		return HttpResponseRedirect("/activities") ;
	if request.method == 'GET': #GET METHOD
		print sessions.getUser(request)
		return render(request, 'participation/login.html', {})
	else: #POST METHOD
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
		updateUserLoginTime(uid)
		return JsonResponse({'status': 'success', 'msg': '登陆成功!'})

@require_http_methods(['GET'])
@csrf_exempt
def logout(request):
	print "Logout!"
	sessions.logout(request) 
	return HttpResponseRedirect('/login')

@require_http_methods(['POST'])
@csrf_exempt
def verification(request):
	#print request.POST
	#return JsonResponse({'status': 'success', 'msg': '实名验证成功！', 'data': {'idnumber': request.POST['id_number']}})
	if not request.POST.has_key('id_number') or not request.POST.has_key('name'):
		return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})

	name = request.POST['name']
	idnumber = request.POST['id_number']
	if len(name) == 0 or len(idnumber) == 0:
		return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})

	veresult, user = verificationOfRealId(name, idnumber) 
	print name, idnumber 
	if veresult == 0:
		return JsonResponse({'status': 'error', 'msg': '实名验证失败！实名或身份证号有误。'})
	if veresult == 2:
		return JsonResponse({'status': 'error', 'msg': '实名验证失败！此身份证已被使用。'})

	user['photo'] = None
	print user
	return JsonResponse({'status': 'success', 'msg': '实名验证成功！', 'data':user})

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def register(request):
	if request.method == 'GET':
		return render(request, 'participation/register.html', {})
	else:
		if not request.POST.has_key('username') or not request.POST.has_key('pwd') or not request.POST.has_key('mobile') or not request.POST.has_key('email'):
			return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})

		username = request.POST['username']
		pwd = request.POST['pwd']
		mobile = request.POST['mobile']
		email = request.POST['email']
		idnumber = request.POST['id_number'] if request.POST.has_key('id_number') else 0
		print "!!!",username
		if len(username) == 0 or len(pwd) == 0 or len(mobile) == 0 or len(email) == 0:
			return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})

		print request.POST
		if False and verificationOfRealId(request.POST['name'], request.POST['id_number']) != 1:
			return JsonResponse({'status': 'error', 'msg': '实名验证失败！您需要重新返回进行验证。'})

		if registeredUsername(username):
			return JsonResponse({'status': 'error', 'msg': '此用户名已被注册，请重新填写'})
		if len(pwd) < 6 or len(username) < 4:
			return JsonResponse({'status': 'error', 'msg': '用户名或密码长度不够（用户名至少4位，密码至少6位）'})
		registerAccount(idnumber, username, pwd, mobile, email)

		uid = getUidByUsername(username)
		identity = getIdentityByUid(uid)
		sessions.login(request, uid, identity)

		return JsonResponse({'status': 'success', 'msg': '注册成功'})


@require_http_methods(['GET'])
@csrf_exempt
@login_required
def activity(request, aaid):
	activity = getActivityByAaid(aaid) 
	if activity == -1:
		raise Http404 
	else:
		uid, identity = sessions.getUser(request)
		record = getRecordByUidAndAaid(uid, aaid)
		print record
		return render(request, 'participation/activity.html', {'activity': activity, 'has_signed_in': record!=-1})

@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
def checkIn(request, aaid):
	if request.method == 'GET':
		return render(request, 'participation/checkin.html', {'aaid': aaid})
	else:
		uid, identity = sessions.getUser(request)
		result = userCheckIn(uid, aaid) ;
		if result == 0:
			return JsonResponse({'status': 'error', 'msg': '签到失败！'})
		elif result == 2:
			return JsonResponse({'status': 'error', 'msg': '您已签到。'})
		else:
			return JsonResponse({'status': 'success', 'msg': '签到成功！'})


@require_http_methods(['GET'])
@csrf_exempt
@login_required
def checkInSuccess(request):
	return render(request, 'participation/checkin_success.html', {})

@require_http_methods(['GET'])
@csrf_exempt
@login_required
def checkInFail(request):
	return render(request, 'participation/checkin_fail.html', {})

@require_http_methods(['POST'])
@csrf_exempt
@login_required
def signIn(request, aaid):
	uid, identity = sessions.getUser(request)
	if(uid == None):
		return JsonResponse({'status': 'error', 'msg': '身份验证出错，请重新登录！'})
	result = userSignIn(uid, aaid) ;
	if result == 0:
		return JsonResponse({'status': 'error', 'msg': '报名失败！'})
	elif result == 2:
		return JsonResponse({'status': 'error', 'msg': '您已报名。'})
	elif result == 3:
		return JsonResponse({'status': 'error', 'msg': '已无报名名额。'})
	else:
		return JsonResponse({'status': 'success', 'msg': '报名成功！'})


@require_http_methods(['GET'])
@login_required
def userActivities(request):
	uid, identity = sessions.getUser(request)
	act = getActivitiesInvolvedByUid(uid)
	#	print act
	return render(request, 'participation/user_activities.html', {'activities':act})


@require_http_methods(['GET'])
@login_required
def userMessages(request):
	uid, identity = sessions.getUser(request)
	message = 0#getBroadcastsReceivedByUid(uid)
	return render(request, 'participation/user_messages.html', {'messages':message})


@require_http_methods(['GET'])
@login_required
def userSettings(request):
	return render(request, 'participation/user_settings.html')

@require_http_methods(['POST'])
@csrf_exempt
@login_required
def setUserInformation(request):
	uid, identity = sessions.getUser(request)
	user = getUserByUid(uid)
	if request.POST['email'] != None:
		user['email'] = request.POST['email']
	if request.POST['mobile'] != None:
		user['mobile'] = request.POST['mobile']
	result = setUserInfo(uid, user)
	if result == 0:
		return JsonResponse({'status': 'error', 'msg': '修改失败！'})
	else:
		return JsonResponse({'status': 'success', 'msg': '修改成功！'})

@require_http_methods(['POST'])
@csrf_exempt
@login_required
def resetPassword(request):
	uid, identity = sessions.getUser(request)
	user = getUserByUid(uid)
	if request.POST['password'] == None or len(request.POST['password']) == 0:
		return JsonResponse({'status': 'error', 'msg': '输入无效！'})
	result = setPassword(uid, request.POST['password'])
	if result == 0:
		return JsonResponse({'status': 'error', 'msg': '修改失败！'})
	else:
		return JsonResponse({'status': 'success', 'msg': '修改成功！'})