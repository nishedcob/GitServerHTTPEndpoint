"""EduNube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from authApp import views

login_template = 'auth/login'
login_template = login_template + ".noreg"
login_template = login_template + ".html"

appname = "authApp"
urlpatterns = [
    url("^logout$", auth_views.logout, {'template_name': 'auth/logout.html', 'next_page': 'auth:login'}, name='logout'),
    url("^login$", auth_views.login, {'template_name': login_template}, name='login'),
    url("^tokens$", views.TokensView.as_view(), name="tokens"),
    url("^token/(?P<app_name>[a-zA-Z_0-9]*).json$", views.TokenView.as_view(), name="token"),
    url("^token/edit/(?P<app_name>[a-zA-Z_0-9]*)$", views.EditTokenView.as_view(), name="edit_token"),
    url("^token/delete/(?P<app_name>[a-zA-Z_0-9]*)$", views.DeleteTokenView.as_view(), name="delete_token"),
    url("^token/secret/(?P<app_name>[a-zA-Z_0-9]*)$", views.SecretTokenView.as_view(), name="secret_token")
]
