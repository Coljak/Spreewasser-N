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
    path('Impressum-Information', views.impressum_information, name='impressum_information'),
    path('Map/', views.map, name='map'), # kann weg
    path('Registration/', views.register, name='registration'),
    path('Login/', LoginView.as_view(), name='user_login'),
    path('Login/Dashboard/', views.user_dashboard, name='user_dashboard'),
    path('Login/Userinfo/', views.userinfo, name='user_info'),
    path('Logout/', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='user_logout'),
    path('testhtml/', views.TestHTML.as_view(), name='testname'),
    path('data.geojson', GeoJSONLayerView.as_view(model=models.ProjectRegion), name='project_region_geojson'),
    path('Chart/', views.ChartView.as_view(), name='chart'), 
    path('chartdata/', views.get_chart, name='chart-api'),
    path('Login/Dashboard/save/', views.save_user_field, name='save-user-field'),
    path('Login/Dashboard/load/', views.get_user_fields, name='get-user-fields'),
    path('Login/Dashboard/update/', views.update_user_field, name='update-user-fields'),
    ]
