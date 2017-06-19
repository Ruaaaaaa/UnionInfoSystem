# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from base.decorators import login_required, admin_required

import json
import os
import xlrd
import xlwt
import datetime
import codecs
import shutil
import zipfile
import reportlab.rl_config
from reportlab.pdfgen import canvas 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
#pdfmetrics.registerFont(TTFont('song', 'SURSONG.TTF'))
#pdfmetrics.registerFont(TTFont('hei', 'SIMHEI.TTF'))

from InfoSystem.shared import dashboard_tabs
from base import sessions
from participation.api import *
from dashboard.api import *
# Create your views here.


def file_iterator(file_name, chunk_size=8192):
	with open(file_name, "rb") as f:
		while True:
			c = f.read(chunk_size)
			if c:
				yield c
			else:
				break

def hello(c):
	name = "郭元晨"
	c.drawString(100,100,name)
	# the two unicode characters below are "Tokyo"

def saveUserInfoToXlsx(dirpath, filename, userlist, activity):
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)
	xlpath = dirpath + '/' + filename
	style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
		num_format_str='#,##0.00')
	style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
	wb = xlwt.Workbook()
	ws = wb.add_sheet('UserList')
	row = 0 
	ws.write(0, 0, '编号')
	ws.write(0, 1, '报名人')
	ws.write(0, 2, '性别')
	ws.write(0, 3, '工号')
	ws.write(0, 4, '邮箱')
	ws.write(0, 5, '手机')
	ws.write(0, 6, '所属单位')
	ws.write(0, 7, '所属子工会')
	ws.write(0, 8, '所属编制')
	if not activity == None:
		ws.write(0, 9, '是否已签到')
	for user in userlist:
		row = row+1
		ws.write(row, 0, row)
		ws.write(row, 1, user['name'])
		ws.write(row, 2, user['sex_text'])
		ws.write(row, 3, user['wid'])
		ws.write(row, 4, user['email'])
		ws.write(row, 5, user['mobile'])
		ws.write(row, 6, user['department_text'])
		ws.write(row, 7, user['sub_union_text'])
		ws.write(row, 8, user['formation_text'])
		if not activity == None:
			record = getRecordByUidAndAaid(user['uid'], activity['aaid'])
			ws.write(row, 9, "是" if record['checked_in'] == True else "否")
	wb.save(xlpath)
	return xlpath

#reportlab中的pagesize为(595.27,841.89)，单位为1/72inch
#都是些什么乱七八糟的单位
def saveUserInfoToPdf(dirpath, filename, userlist, activity):
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)
	pdfpath = dirpath + '/' + filename
	print "pdf:", pdfpath 
	canv = canvas.Canvas(pdfpath)
	canv.setFont('STSong-Light', 11)
	#hello(canv)	
	h = 841.89; w = 595.27
	pw = 70.87; ph = 99.21
	mw = 81; mh = 122 
	r = 1; c = 1 
	for user in userlist:
		record = getRecordByUidAndAaid(user['uid'], activity['aaid'])
		#if record['checked_in'] == False:
		#	continue
		photopath = str(user['photo'])
		if len(photopath) == 0:
			photopath = "photos/None/no-img.jpg"
		photopath = "../media/"+photopath
		photopath = 'media/'+photopath	
		y = h-59.945-mh*r; x = 19.135+mw*(c-1)
		canv.drawImage(photopath, x, y+22, width=pw,height=ph)
		canv.drawString(x, y+12, user['name'])
		c = c+1 
		if c == 8:
			r = r+1; c = 1 
			if r == 7:
				canv.showPage()
				canv.setFont('STSong-Light', 11)
				r = 1
	canv.showPage()
	canv.save()
	return pdfpath

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def login(request):

	# 如果已经管理员session，转到activity
	# 如果已经普通用户session，转到404
	# 否则，再渲染登录界面

	if request.method == 'GET':
		user = sessions.getUser(request)
		print user
		print getIdentityByUid(user[0])
		if user[0] == None or user[1] == None:
			return render(request, 'dashboard/login.html', {})
		else:
			if user[1] == 1:
				raise Http404
			else:
				return HttpResponseRedirect('/admin/activity')
	else:
		if not request.POST.has_key('username') or not request.POST.has_key('pwd'):
			return JsonResponse({'status': 'error', 'msg': '请输入用户名和密码。'})
		username = request.POST['username'] 
		pwd = request.POST['pwd']

		uid = getUidByUsername(username)
		if uid == -1: # no such username 
			return JsonResponse({'status': 'error', 'msg': '没有这个账号!'})
		if verifyPassword(uid, pwd) == False:
			return JsonResponse({'status': 'error', 'msg': '用户名或密码错误!'})
		identity = getIdentityByUid(uid)
		if sessions.login(request, uid, identity) == False:
			return JsonResponse({'status': 'error', 'msg': '登录失败!'})
		return JsonResponse({'status': 'success', 'msg': '登陆成功!'})
		


@require_http_methods(['GET'])
@login_required
@admin_required
def activity(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	act_list = getActivitiesByUidSimple(uid)
	return render(request, 'dashboard/activity.html', {'tab': dashboard_tabs['activity'], 'username': username, 'activities': act_list})



@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
@admin_required
def newActivity(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	if request.method == 'GET':
		return render(request, 'dashboard/new_activity.html', {'tab': dashboard_tabs['activity'], 'type': 'new', 'username': username})
	else:
		act_attributes = json.loads(request.POST['data'])
		imagefile = request.FILES['poster']
		if imagefile == None:
			return JsonResponse({'status': 'error', 'msg': '没有收到活动海报'})	
		act_attributes['filename'] = imagefile.name
		act_attributes['image'] = ContentFile(imagefile.read())
		create_result = createNewActivity(uid, act_attributes)
		if create_result['status'] == "error":
			JsonResponse({'status': 'error', 'msg': create_result['msg']})
		else:
			return JsonResponse({'status': 'success', 'msg': '创建活动成功!', 'data': {'aaid': create_result['aaid']} })



@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
@admin_required
def editActivity(request, aaid):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	activity = getActivityByAaid(aaid)	
	if activity == -1: 
		raise Http404
	if request.method == 'GET':
		return render(request, 'dashboard/new_activity.html', {'tab': dashboard_tabs['activity'], 'activity': activity, 'username': username, 'type': 'edit'})
	else:
		act_attributes = json.loads(request.POST['data'])
		act_attributes ['aaid'] = aaid
		authority = activityAuthorityCheck(uid, aaid)
		if authority == -1:
			return JsonResponse({'status': 'error', 'msg': '无此活动！'})
		elif authority == 0:
			return JsonResponse({'status': 'error', 'msg': '您无权修改此活动！'})

		imagefile = request.FILES['poster']
		if imagefile == None:
			return JsonResponse({'status': 'error', 'msg': '没有收到活动海报'})	
		act_attributes['filename'] = imagefile.name
		act_attributes['image'] = ContentFile(imagefile.read())
		editresult = doEditActivity(uid, act_attributes)
		if editresult == 0:
			return JsonResponse({'status': 'error', 'msg': '修改活动失败！'})
		else: 
			return JsonResponse({'status': 'success', 'msg': '修改活动成功!'})	



@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def deleteActivity(request, aaid):
	uid = sessions.getUser(request)[0] 
	authority = activityAuthorityCheck(uid, aaid)
	if authority == -1:
		return JsonResponse({'status': 'error', 'msg': '无此活动！'})
	elif authority == 0:
		return JsonResponse({'status': 'error', 'msg': '您无权删除此活动！'})
	deleteresult = doDeleteActivity(uid, aaid)
	if deleteresult == 0:
		return JsonResponse({'status': 'error', 'msg': '删除活动失败！'})
	else:
		return JsonResponse({'status': 'success', 'msg': '删除活动成功!'})	



@require_http_methods(['GET'])
@login_required
@admin_required
def downloadActivity(request, aaid): 

	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	if activityAuthorityCheck(uid, aaid) != 1:
		return JsonResponse({'status': 'error', 'msg': '无权下载此活动信息！'})

	#excel part
	dirpath = r"media/files/%s"%aaid
	xlname = "已报名用户信息.xls"
	pdfname = "已报名用户.pdf"
	activity = getActivityByAaid(aaid)
	userlist, page_total = getUserListByFilter(1, 10000000, [], [], [activity['aid']], 0)	
	if not os.path.exists(dirpath): #reset dir
		os.makedirs(dirpath)
	else:
		shutil.rmtree(dirpath)
	pdfpath = saveUserInfoToPdf(dirpath, pdfname, userlist, activity)
	xlpath = saveUserInfoToXlsx(dirpath, xlname, userlist, activity)

	#txt part
	txtfile = codecs.open(dirpath+'/活动信息.txt', 'w', 'utf-8') 
	string = '活动名称：\n'+activity['title']+'\n' 
	txtfile.write('活动名称：\r\n'+activity['title']+'\r\n')
	txtfile.write('活动简介：\r\n'+activity['description']+'\r\n')
	txtfile.write('活动内容：\r\n'+activity['content']+'\r\n') 
	txtfile.write('活动报名人数：\r\n'+str(activity['signin_count'])+'\r\n') 
	txtfile.write('活动签到人数：\r\n'+str(activity['checkin_count'])+'\r\n') 
	txtfile.close()

	#photopart
	if not os.path.exists(dirpath+'/photos'):
		os.makedirs(dirpath+'/photos')
	for user in userlist:
		record = getRecordByUidAndAaid(user['uid'], activity['aaid'])
		if record['checked_in'] == False:
			continue
		photopath = str(user['photo'])
		if len(photopath) == 0:
			photopath = "photos/None/no-img.jpg"
		#photopath = "../media/"+photopath
		photopath = 'media/'+photopath
		shutil.copyfile(photopath, dirpath+'/photos/'+user['name']+'.jpg')

	#zippart
	zipf = zipfile.ZipFile(dirpath+'/package.zip', 'w')
	zipf.write(dirpath+'/已报名用户信息.xls', '已报名用户信息.xls')
	zipf.write(dirpath+'/活动信息.txt', '活动信息.txt')
	for subdirpath, subdirnames, filenames in os.walk(dirpath+'/photos'): 
		for filename in filenames: 
			zipf.write(os.path.join(subdirpath,filename), '用户照片/'+filename) 
	zipf.close()

	response = StreamingHttpResponse(file_iterator(dirpath+'/package.zip'))
	restr = u'attachment;filename="%s_%s.zip'%(aaid, '活动信息')
	clientSystem = request.META['HTTP_USER_AGENT']
	if clientSystem.find('Windows') > -1:
		restr = restr.encode('cp936')
	else:
		restr = restr.encode('utf-8')
	response['Content-Disposition'] = restr
	return response

@require_http_methods(['GET'])
@login_required
@admin_required
def users(request):
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	return render(request, 'dashboard/users.html', {'tab': dashboard_tabs['users'], 'username': username})

@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def getUsers(request):
	dic = json.loads(request.body)
	try:
		page = dic['page']
		number = dic['number']
		departments = dic['departments']
		sub_unions = dic['sub_unions']
		activities = dic['activities']
		checked_in = dic['checked_in']
	except Exception,e:  
		return JsonResponse({'status': 'error', 'msg': e})
	#page_total = getUserPageCount(number)
	user_list, page_total = getUserListByFilter(page, number, departments, sub_unions, activities, checked_in)
	return JsonResponse({'status': 'success', 'msg': 'users', 'data':{'page_total':page_total, 'user_list':user_list}})


#先不管了，弃疗
@require_http_methods(['GET'])
@login_required
@admin_required
def downloadUsers(request):	
	uid = sessions.getUser(request)[0] 
	username = getUsernameByUid(uid)
	file_name = "dashboard/files/1.txt"
	response = StreamingHttpResponse(file_iterator(file_name))
	response['Content-Type'] = 'application/octet-stream'
	response['Content-Disposition'] = 'attachment;filename="userlist.txt"'
	return response

	#return JsonResponse({'status': 'success', 'msg': 'download'})


@require_http_methods(['GET'])
@login_required
@admin_required
def broadcast(request):
	return render(request, 'dashboard/broadcast.html', {'tab': dashboard_tabs['broadcast']})


@require_http_methods(['GET'])
@login_required
@admin_required
def organization(request):
	return render(request, 'dashboard/organization.html', {'tab': dashboard_tabs['organization']})


@require_http_methods(['GET'])
@login_required
@admin_required
def getActivities(request):
	return JsonResponse({'status':'success', 'msg': '获取活动列表成功！', 'data': {'activities': getActivityListSimple()}})

@require_http_methods(['GET'])
@login_required
@admin_required
def getActivityContent(request, aaid):
	activity = getActivityByAaid(aaid) 
	if activity == -1:
		JsonResponse({'status':'error', 'msg': '无此活动！'})
	return JsonResponse({'status':'success', 'msg': '获取活动详情成功！', 'data': {'content': activity['content']}})

@require_http_methods(['GET'])
@login_required
@admin_required
def getSubUnions(request):
	return JsonResponse({'status':'success', 'msg': '获取分工会列表成功！', 'data': {'subunions': getSubUnionListSimple()}})


@require_http_methods(['GET'])
@login_required
@admin_required
def getDepartments(request):
	return JsonResponse({'status':'success', 'msg': '获取部门列表成功！', 'data': {'departments': getDepartmentListSimple()}})


@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def newBroadcast(request):
	dic = json.loads(request.body)
	dic['uid'] = sessions.getUser(request)[0]
	create_result = createBroadcast(dic)
	if create_result['status'] == "error":
		JsonResponse({'status': 'error', 'msg': create_result['msg']})
	else:
		return JsonResponse({'status': 'success', 'msg': '消息发送成功！'})


@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def getBroadcast(request):
	dic = json.loads(request.body)
	try:
		page = dic['page']
		number = dic['number']
	except Exception,e:  
		return JsonResponse({'status': 'error', 'msg': e})
	old_news_list, page_total = getBroadcastByPage(page, number)
	return JsonResponse({'status': 'success', 'msg': 'users', 'data':{'page_total':page_total, 'old_news_list':old_news_list}})


@require_http_methods(['GET'])
@login_required
@admin_required
def getDateTime(request):
	return JsonResponse({'status':'success', 'msg': '获取日期与时间成功！', 'data': {'date_time': datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}})

@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def addSubunion(request):
	name = request.POST['name']
	if name == None or len(name) == 0:
		return JsonResponse({'status': 'error', 'msg': '输入信息不完整！'})
	result = doAddSubunion(name)
	if result == 0 :
		return JsonResponse({'status': 'error', 'msg': '添加部门失败！已有此子工会！'})
	else:
		return JsonResponse({'status': 'success', 'msg': '添加子工会成功！'})
	
@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def addDepartment(request):
	name = request.POST['name']
	suid = request.POST['suid']
	if name == None or len(name) == 0 or suid == None:
		return JsonResponse({'status': 'error', 'msg': '输入信息不完整！'})
	result = doAddDepartment(name, suid)
	if result == 0:
		return JsonResponse({'status': 'error', 'msg': '添加部门失败！已有此部门！'})
	else:
		return JsonResponse({'status': 'success', 'msg': '添加部门成功！'})
	
@require_http_methods(['POST'])
@csrf_exempt
@login_required
@admin_required
def setDepartmenttoSubunion(request):
	did = request.POST['did']
	suid = request.POST['suid']
	if did == None or suid == None:
		return JsonResponse({'status': 'error', 'msg': '输入信息不完整！'})
	result = doSetDepartmenttoSubunion(did, suid)
	if result == 0:
		return JsonResponse({'status': 'error', 'msg': '修改部门所属子工会失败！'})
	else:
		return JsonResponse({'status': 'success', 'msg': '修改部门所属子工会成功！'})
	
