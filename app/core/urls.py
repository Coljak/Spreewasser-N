from django.contrib import admin
from django.urls import include, path

from django.contrib.auth.views import LoginView
from . import views

# template tagging
app_name = 'core'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='core-index'),
    path('SpreewasserN/', views.form_sidebar, name='form-sidebar'),
    #path('Home/', views.home, name='home'),
    # path('Home/', views.IndexView.as_view(), name='home'),
    path('Map/', views.map, name='map'),
    path('Registration/', views.register, name='registration'),
    path('Login/', LoginView.as_view(), name='user_login'),
    path('Login/Dashboard/', views.user_dashboard, name='user_dashboard'),
    path('Login/Userinfo/', views.userinfo, name='user_info'),
        #path('user_login/', views.user_login, name='user_login'),
    path('Logout/', views.user_logout, name='user_logout'),
    path('testhtml/', views.TestHTML.as_view(), name='testname'),

]
