"""raspimapper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path, include
import debug_toolbar
admin.site.site_header = 'Mapper Admin'
admin.site.index_title = 'My Admin Panel'

urlpatterns = [  
    path('', RedirectView.as_view(url='bots/home/')),
    path('admin/', RedirectView.as_view(url='../bots/admin/')),
    path('bots/', include('bots.urls')),
    path('playground', include('playground.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('grammar/', include('grammar.urls')),
]
