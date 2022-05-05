from django.contrib import admin 
from django.urls import path, include
from . import views
from rest_framework import routers
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import restapi

router = routers.DefaultRouter()
urlpatterns = [ 
    path('api/', include(router.urls)),
    path('form/', views.FormView, name='form'),
    path('', views.HomeView, name='home')
]
#urlpatterns += staticfiles_urlpatterns()

