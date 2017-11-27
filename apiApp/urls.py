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
    url('^ns/create/(?P<namespace>[a-zA-Z0-9]*)/$', views.CreateNamespaceView.as_view(), name='create_ns'),
    url('^ns/edit/(?P<namespace>[a-zA-Z0-9]*)/$', views.EditNamespaceView.as_view(), name='edit_ns'),
    url('^repo/create/(?P<namespace>[a-zA-Z0-9]*)/(?P<repository>[a-zA-Z0-9]*)/$', views.CreateRepositoryView.as_view(),
        name='create_repo'),
    url('^repo/edit/(?P<namespace>[a-zA-Z0-9]*)/(?P<repository>[a-zA-Z0-9]*)/$', views.EditRepositoryView.as_view(),
        name='edit_repo'),
    url('^file/create/(?P<namespace>[a-zA-Z0-9]*)/(?P<repository>[a-zA-Z0-9]*)/(?P<file_path>[a-zA-Z0-9/]*\.[a-zA-Z0-9]'
        '*)$', views.CreateFileView.as_view(), name='create_file'),
    url('^file/edit/mv/(?P<namespace>[a-zA-Z0-9]*)/(?P<repository>[a-zA-Z0-9]*)/(?P<file_path>[a-zA-Z0-9/]*\.[a-zA-Z0-9'
        ']*)$', views.MoveEditFileView.as_view(), name='move_file'),
    url('^file/edit/contents/(?P<namespace>[a-zA-Z0-9]*)/(?P<repository>[a-zA-Z0-9]*)/(?P<file_path>[a-zA-Z0-9/]*\.[a-z'
        'A-Z0-9]*)$', views.ContentsEditFileView.as_view(), name='edit_file'),
]
