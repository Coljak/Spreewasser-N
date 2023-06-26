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
    path('', include('django.contrib.auth.urls')),
    
    path('sign-up/', views.sign_up, name='sign_up'),
    path('Impressum-Information/', views.impressum_information, name='impressum_information'),
    path('Timelapse/', views.timelapse, name='timelapse'),
    path('TimelapseC/', views.timelapse_c, name='timelapse-c'),
    # path('sidebar/', views.sidebar, name='sidebar'),
    path('thredds/', views.thredds_wms_view, name='thredds-wms'),
    # path('Registration/', views.register, name='registration'),
    # path('map/', LoginView.as_view(), name='map'),
    # path('Login/', views.user_login, name='user_login'),
    path('login/Dashboard/', views.user_dashboard, name='user_dashboard'),
    path('Login/Userinfo/', views.userinfo, name='user_info'),
    path('login/Dashboard/get-csrf-token/', views.get_csrf_token, name='get-csrf-token'),
    path('login/Dashboard/save/', views.save_user_field, name='save-user-field'),
    path('login/Dashboard/load/', views.get_user_fields, name='get-user-fields'),
    path('login/Dashboard/loadasync/', views.get_user_fields_async, name='get-user-fields-async'),
    path('login/Dashboard/saveasync/', views.save_user_field_async, name='save-user-fields-async'),
    path('login/Dashboard/update/', views.update_user_field, name='update-user-fields'),
    path('login/Dashboard/delete/<int:id>', views.delete_user_field, name='delete-user-field'),
    # path('Logout/', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='user_logout'),  
    path('data.geojson', GeoJSONLayerView.as_view(model=models.ProjectRegion), name='project_region_geojson'),
    path('Chart/', views.ChartView.as_view(), name='chart'), 
    path('login/Dashboard/chartdata/<int:crop_id>', views.get_chart, name='chart-api'),
    path('login/Dashboard/monica-map/', views.thredds_wms_view, name='monica-map'),
    # Bootstrap test colors
    path('bootstrap', views.bootstrap, name='bootstrap'),
    ]
