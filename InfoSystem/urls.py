"""InfoSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views import static
from dashboard import views as dashboard
from participation import views as participation
from base import views as base
import settings

urlpatterns = [
    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^administrator/', admin.site.urls),
	# User part
    url(r'^login', participation.login),
    url(r'^logout', participation.logout),
    url(r'^register', participation.register),
    url(r'^verification', participation.verification),
    url(r'^activity/([0-9, a-z]{10})/$', participation.activity),
    url(r'^activity/([0-9, a-z]{10})/checkin$', participation.checkIn),
    url(r'^activity/checkin/success$', participation.checkInSuccess),
    url(r'^activity/checkin/fail$', participation.checkInFail),
    url(r'^activity/([0-9, a-z]{10})/signin$', participation.signIn),
    
    # Admin part
    url(r'^admin/login', dashboard.login),
    url(r'^admin/activity$', dashboard.activity),
    url(r'^admin/activity/new$', dashboard.newActivity),
    url(r'^admin/activity/([0-9, a-z]{10})/edit$', dashboard.editActivity),
    url(r'^admin/activity/([0-9, a-z]{10})/delete', dashboard.deleteActivity),
    url(r'^admin/activity/([0-9, a-z]{10})/download$', dashboard.downloadActivity),
    url(r'^admin/users$', dashboard.users),
    url(r'^admin/users/get', dashboard.getUsers),
    url(r'^admin/activities/get', dashboard.getActivities),
    url(r'^admin/departments/get', dashboard.getDepartments),
    url(r'^admin/subunions/get', dashboard.getSubUnions),
    url(r'^admin/users/download$', dashboard.downloadUsers),
    url(r'^admin/broadcast$', dashboard.broadcast),
    url(r'^admin/broadcast/new', dashboard.newBroadcast),
    url(r'^admin/broadcast/get', dashboard.getBroadcast),
    url(r'^admin/get_date_time', dashboard.getDateTime)   
]
