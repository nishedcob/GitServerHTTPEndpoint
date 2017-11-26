"""GitServerHTTPEndpoint URL Configuration

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

from apiApp import views

appname = 'apiApp'
urlpatterns = [
    url('ns/create/(?P<namespace>[a-zA-Z0-9])/$', views.CreateNamespaceView.as_view(), 'create_ns'),
    url('ns/edit/(?P<namespace>[a-zA-Z0-9])/$', views.EditNamespaceView.as_view(), 'edit_ns'),
    url('repo/create/(?P<namespace>[a-zA-Z0-9])/(?P<repository>)/$', views.CreateRepositoryView.as_view(),
        'create_repo'),
    url('repo/edit/(?P<namespace>[a-zA-Z0-9])/(?P<repository>)/$', views.EditRepositoryView.as_view(), 'edit_repo'),
]
