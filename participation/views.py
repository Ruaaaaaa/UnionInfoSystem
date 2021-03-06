# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
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
		return HttpResponseRedirect("/") ;
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

	veresult = verificationOfRealId(name, idnumber) ;
	print name, idnumber 
	if veresult == 0:
		return JsonResponse({'status': 'error', 'msg': '实名验证失败！实名或身份证号有误。'})
	if veresult == 2:
		return JsonResponse({'status': 'error', 'msg': '实名验证失败！此身份证已被使用。'})

	return JsonResponse({'status': 'success', 'msg': '实名验证成功！', 'data': {'id_number': idnumber}})

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
	return render(request, 'participation/activity.html', {'activity': activity})

@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
def checkIn(request, aaid):
	if request.method == 'GET':
		return render(request, 'participation/checkin.html', {'aaid': aaid})
	else:
		uid = request.sessions['uid']
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
	else:
		return JsonResponse({'status': 'success', 'msg': '报名成功！'})
