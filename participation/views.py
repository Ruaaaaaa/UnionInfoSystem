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
	if request.method == 'GET':
		return render(request, 'participation/login.html', {})
	else:
		return JsonResponse({'status': 'success', 'msg': 'success'});


@require_http_methods(['GET', 'POST'])
def register(request):
	return render(request, 'participation/register.html', {})


@require_http_methods(['GET'])
@login_required
def activity(request, aaid):
	return render(request, 'participation/activity.html', {'aaid': aaid})


@require_http_methods(['GET', 'POST'])
@login_required
def checkin(request, aaid):
	return render(request, 'participation/checkin.html', {'aaid': aaid})


@require_http_methods(['GET'])
@login_required
def checkinSuccess(request):
	return render(request, 'participation/checkin_success.html', {})


@require_http_methods(['GET'])
@login_required
def checkinFail(request):
	return render(request, 'participation/checkin_fail.html', {})

