# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from base import api

# Create your views here.

def login(request):
    return render(request, 'login.html', {'title': '用户登陆'})