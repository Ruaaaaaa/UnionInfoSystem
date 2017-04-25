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
import md5

# Create your views here.

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def login(request):
	if request.method == 'GET': #GET METHOD
		return render(request, 'participation/login.html', {})
	else: #POST METHOD
		if not request.has_key('username') or not request.has_key('pwd'):
			return JsonResponse({'status': 'error', 'msg': '请输入用户名和密码。'})
		username = request['username'] 
		pwd = request['pwd']
		uid = getUidByName(username)
		if uid == -1: # no such username 
			return JsonResponse({'status': 'error', 'msg': '没有这个账号!'})
		if verifyPassword(uid, pwd) == False:
			return JsonResponse({'status': 'error', 'msg': '用户名或密码错误!'})
		identity = getIdentityByUid(uid)
		if sessions.login(request, uid, identity) == False:
			return JsonResponse({'status': 'error', 'msg': '登录失败!'})
		return JsonResponse({'status': 'success', 'msg': '登陆成功!'})

@require_http_methods(['GET'])
@csrf_exempt
@login_required 
def logout(request):
	sessions.logout(request) 
	return HttpResponseRedirect('/login')

@require_http_methods(['POST'])
@csrf_exempt
def verification(request):
	if not request.has_key('idnumber') or not request.has_key('realname'):
		return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})

	realname = request['realname']
	idnumber = request['idnumber']
	if realname.len() == 0 or idnumber.len() == 0:
		return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})

	midnumber = md5.new()   
	midnumber.update(idnumber)   
	idnumber = midnumber.hexdigest()  


	veresult = verificationOfRealId(realname, idnumber) ;
	if veresult == 0:
		return JsonResponse({'status': 'error', 'msg': '实名验证失败！实名或身份证号有误。'})
	if veresult == 2:
		return JsonResponse({'status': 'error', 'msg': '实名验证失败！此身份证已被使用。'})

	return JsonResponse({'status': 'success', 'msg': '实名验证成功！', 'data': {'idnumber': idnumber}})

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def register(request):
	if request.method == 'GET':
		return render(request, 'participation/register.html', {})
	else:
		if not request.has_key('username') or not request.has_key('pwd'):
			return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})

		username = request['username']
		pwd = request['pwd']
		if username.len == 0 or pwd.len == 0:
			return JsonResponse({'status': 'error', 'msg': '请填写完您的信息。'})
		mpwd = md5.new()   
		mpwd.update(pwd)   

		if verificationOfRealId(request['realname'], request['idnumber']) != 1:
			return JsonResponse({'status': 'error', 'msg': '实名验证失败！您需要重新返回进行验证。'})

		if registeredUsername(username):
			return JsonResponse({'status': 'error', 'msg': '此用户名已被注册，请重新填写'})
		if pwd.len() < 6 or username.len() < 4:
			return JsonResponse({'status': 'error', 'msg': '用户名或密码长度不够（用户名至少4位，密码至少6位）'})

		registerAccount(idnumber, username, mpwd.hexdigest())

@require_http_methods(['GET'])
@csrf_exempt
@login_required
def activity(request, aaid):
	Act = getActivityByAaid(aaid) 
	return render(request, 'participation/activity.html', {'aaid': Act})

@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
def checkin(request, aaid):
	if request.method == 'GET':
		return render(request, 'participation/checkin.html', {'aaid': aaid})
	else:
		uid = request.sessions['uid']
		result = userCheckin(uid, aaid) ;
		if result == 0:
			return JsonResponse({'status': 'error', 'msg': '签到失败！'})
		elif result == 2:
			return JsonResponse({'status': 'error', 'msg': '您已签到。'})
		else:
			return JsonResponse({'status': 'error', 'msg': '签到成功！'})


@require_http_methods(['GET'])
@csrf_exempt
@login_required
def checkinSuccess(request):
	return render(request, 'participation/checkin_success.html', {})

@require_http_methods(['GET'])
@csrf_exempt
@login_required
def checkinFail(request):
	return render(request, 'participation/checkin_fail.html', {})

