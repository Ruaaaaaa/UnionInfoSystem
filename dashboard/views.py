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

# Create your views here.

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def login(request):
	# 如果已经管理员session，转到activity
	# 如果已经普通用户session，转到404
	# 否则，再渲染登录界面
	return render(request, 'dashboard/login.html', {})


@require_http_methods(['GET'])
@login_required
@admin_required
def activity(request):
	return render(request, 'dashboard/activity.html', {})


@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
@admin_required
def newActivity(request):
	return render(request, 'dashboard/new_activity.html', {'type': 'new'})


@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
@admin_required
def editActivity(request, aaid):
	return render(request, 'dashboard/new_activity.html', {'type': 'edit'})


@require_http_methods(['GET'])
@login_required
@admin_required
def downloadActivity(request, aaid):
	return JsonResponse({'status': 'success', 'msg': 'download'})


@require_http_methods(['GET'])
@login_required
@admin_required
def users(request):
	return render(request, 'dashboard/users.html', {})


@require_http_methods(['GET'])
@login_required
@admin_required
def getUsers(request):
	return JsonResponse({'status': 'success', 'msg': 'users'})


@require_http_methods(['GET'])
@login_required
@admin_required
def downloadUsers(request):
	return JsonResponse({'status': 'success', 'msg': 'download'})


@require_http_methods(['GET'])
@login_required
@admin_required
def broadcast(request):
	return render(request, 'dashboard/broadcast.html', {})