from django.contrib import admin 
from django.urls import path, include
from . import views
from rest_framework import routers

import restapi

router = routers.DefaultRouter()
urlpatterns = [ 
    path('api/', include(router.urls)),
    path('form/', views.FormView, name='form'),
    path('', views.HomeView, name='home')
]