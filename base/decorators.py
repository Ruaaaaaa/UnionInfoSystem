"""
Decorators.
"""


from django.http import Http404
from base import sessions
from InfoSystem.shared import identities
from django.http import HttpResponseRedirect


def login_required(function):
    def wrap(request, *args, **kwargs):
        (uid, identity) = sessions.getUser(request)
        if (not uid) or (not identity):
            return HttpResponseRedirect('/login?from=' + request.get_full_path())
        else:
            return function(request, *args, **kwargs)
    return wrap


def admin_required(function):
	def wrap(request, *args, **kwargs):
		(uid, identity) = sessions.getUser(request)
		if uid and (identity is identities['admin']):
			return function(request, *args, **kwargs)
		else:
			raise Http404
	return wrap