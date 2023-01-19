from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from django.contrib.auth.views import LoginView, LogoutView
from djgeojson.views import GeoJSONLayerView
from . import views
from . import models

# template tagging
app_name = 'swn'

urlpatterns = [
    
    path('', views.IndexView.as_view(), name='swn_index'),
    path('SpreewasserN/', views.form_sidebar, name='form_sidebar'),
    #path('Home/', views.home, name='home'),
    # path('Home/', views.IndexView.as_view(), name='home'),
    path('Map/', views.map, name='map'),
    path('Registration/', views.register, name='registration'),
    path('Login/', LoginView.as_view(), name='user_login'),
    path('Login/Dashboard/', views.user_dashboard, name='user_dashboard'),
    path('Login/Userinfo/', views.userinfo, name='user_info'),
        #path('user_login/', views.user_login, name='user_login'),
    # path('Logout/', views.user_logout, name='user_logout'),
    path('Logout/', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='user_logout'),
    path('testhtml/', views.TestHTML.as_view(), name='testname'),
    path('data.geojson', GeoJSONLayerView.as_view(model=models.ProjectRegion), name='project_region_geojson'),

]
