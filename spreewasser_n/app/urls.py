from django.contrib import admin
from django.urls import path, include

from . import views

# template tagging
app_name = 'app'

urlpatterns = [
    #path('', views.index, name='index'),
    path('SpreewasserN/', views.form_sidebar, name='form_sidebar'),
    path('Userinfo/', views.userinfo, name='Userinfo'),
    path('Userproject/', views.userproject, name='Userproject'),
    path('Login/', views.login, name='Login'),
    path('Home/', views.home, name='Home'),
    path('Map/', views.map, name='Map'),

]

