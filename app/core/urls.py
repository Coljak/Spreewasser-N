from django.contrib import admin
from django.urls import include, path

from django.contrib.auth.views import LoginView
from . import views

# template tagging
app_name = 'app'

urlpatterns = [
    #path('', views.index, name='index'),
    path('SpreewasserN/', views.form_sidebar, name='form_sidebar'),
    path('Home/', views.home, name='Home'),
    path('Map/', views.map, name='Map'),
    path('Registration/', views.register, name='Registration'),
    path('Login/', LoginView.as_view(), name='user_login'),
    path('Login/Dashboard/', views.user_dashboard, name='user_dashboard'),
    path('Login/Userinfo/', views.userinfo, name='Userinfo'),

]
