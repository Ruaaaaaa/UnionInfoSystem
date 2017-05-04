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
		print '无此用户'
		return 0
   
	if not activityAuthorityCheck(uid, aaid):
		print '无权删除此活动'
		return 0
   
	try:
		act = Activity.objects.get(aaid = aaid)
	except ObjectDoesNotExist:
		print '无此活动'
		return 0
	act.delete() 	
	return 1
