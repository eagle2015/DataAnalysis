__author__ = 'jjzhu'
from django.conf.urls import patterns, url
from weibo import views

urlpatterns = patterns('',
                       url(r'^start/$', views.start, name='start'),
                       )
