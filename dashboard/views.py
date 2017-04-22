# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.views.decorators.http import require_http_methods
from base.decorators import login_required, admin_required

from base import sessions

# Create your views here.

@require_http_methods(['GET', 'POST'])
def login(request):
	return render(request, 'dashboard/login.html', {'title': '管理员登陆'})