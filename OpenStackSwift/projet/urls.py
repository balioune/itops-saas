from django.conf.urls import url
from swift import views

urlpatterns = [
	url(r'^$',views.login),
	url(r'^index.html$',views.index),
	url(r'^login$',views.login,name='login'),
	url(r'^login.html$',views.login,name='login'),
	url(r'^swift.html$',views.swift,name='swift'),
    ]
