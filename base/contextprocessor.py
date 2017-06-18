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
import participation.api as api

def common(request):
	uid, identity = sessions.getUser(request)
	print uid 
	if uid == None:
		return {}
	else:
		user = api.getUserByUid(uid)
		print user
		return {'userinfo':user}
