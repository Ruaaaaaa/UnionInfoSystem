# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base import sessions
import participation.api as api
from InfoSystem.shared import DOMAIN

def common(request):
	params = {}
	params['DOMAIN'] = DOMAIN
	uid, identity = sessions.getUser(request)
	if uid != None:
		user = api.getUserByUid(uid)
		params['userinfo'] = user
	return params
