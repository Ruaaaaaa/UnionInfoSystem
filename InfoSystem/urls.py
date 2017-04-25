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
from dashboard import views as dashboard
from participation import views as participation
from base import views as base

urlpatterns = [
	# User part
    url(r'^login', participation.login),
    url(r'^logout', participation.logout),
    url(r'^register', participation.register),
    url(r'^activity/([0-9]{8})/$', participation.activity),
    url(r'^activity/([0-9]{8})/checkin$', participation.checkin),
    url(r'^activity/checkin/success$', participation.checkinSuccess),
    url(r'^activity/checkin/fail$', participation.checkinFail),
    
    # Admin part
    url(r'^admin/login', dashboard.login),
]
