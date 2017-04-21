from InfoSystem.shared import identities


def login(request, uid, identity):
	if identity not in identities.values():
		print 'Invalid identity.'
		return False
	request.session['uid'] = uid
	request.session['identity'] = identity
	return True

def logout(request):
	try:
		del request.session['uid']
		del request.session['identity']
		return True
	except:
		print 'User not logged in.'
		return False


def getUser(request):
	uid = request.session['uid'] if 'uid' in request.session else None
	identity = request.session['identity'] if 'uid' in request.session else None
	return (uid, identity)