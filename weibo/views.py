from django.shortcuts import render_to_response
from django.http import *
from weibo.weibocrawler import WeiboCrawler


def start(request):
    my = WeiboCrawler("", "")
    my.start()
    return