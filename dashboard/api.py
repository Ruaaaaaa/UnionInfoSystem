# -*- coding: utf-8 -*-
"""
Database interface for views.py
"""

from __future__ import unicode_literals
from base.models import *
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import model_to_dict
from participation.api import *
import datetime
import hashlib


def getActivityListSimple():
	activities = Activity.objects.all()
	actlist = []
	for act in activities:
		temp = model_to_dict(act, fields = ['aid', 'title'])
		result = {}
		result['id'] = temp['aid']
		result['text'] = temp['title']
		actlist.append(result)
	return actlist


def getSubUnionListSimple():
	subunions = Subunion.objects.all()
	sublist = []
	for sub in subunions:
		temp = model_to_dict(sub)
		result = {}
		result['id'] = temp['suid']
		result['text'] = temp['name']
		sublist.append(result)
	return sublist


def getDepartmentListSimple():
	departments = Department.objects.all()
	deplist = []
	for depart in departments:
		temp = model_to_dict(depart)
		result = {}
		result['id'] = temp['did']
		result['text'] = temp['name']
		deplist.append(result)
	return deplist


def doDeleteActivity(uid, aaid):
	try:
		user = User.objects.get(uid = uid)
	except ObjectDoesNotExist:
		print 'No such user.'
		return 0
   
	if not activityAuthorityCheck(uid, aaid):
		print 'Insufficient permissions for deleting this activity.'
		return 0
   
	try:
		act = Activity.objects.get(aaid = aaid)
	except ObjectDoesNotExist:
		print 'No such activity.'
		return 0
	act.delete() 	
	return 1

def doAddDepartment(name, suid):
	name.strip()
	try:
		department = Department.objects.get(name = name)
		print u'Department already exist.'
		return 0 
	except ObjectDoesNotExist:
		subunion = Subunion.objects.get(suid = suid)
		#print model_to_dict(subunion)
		department = Department(
			subunion = subunion,
			name = name
   		)
   	 	department.save() 
   	 	return 1 

def doAddSubunion(name):
	try:
		subunion = Subunion.objects.get(name = name)
		print u'Subunion already exist.'
		return 0 
	except ObjectDoesNotExist:
		name.strip()
		subunion = Subunion(
			name = name
   		)
   	 	subunion.save() 
   	 	return 1	

def doSetDepartmenttoSubunion(did, suid):
	try:
		subunion = Subunion.objects.get(suid = suid)
	except ObjectDoesNotExist:
		print u"No such subunion."
		return 0
	try:
		department = Department.objects.get(did = did)
	except ObjectDoesNotExist:
		print u"No such department."
		return 0
	department.subunion = subunion
	department.save() 
	return 1
	