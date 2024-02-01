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
    path('favicon.ico', views.favicon_view, name='favicon'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('Impressum-Information/', views.ImpressumView.as_view(), name='impressum_information'),
    path('acknoledgements/', views.AcknoledgementsView.as_view(), name='acknoledgements'),
    path('Timelapse_test/', views.timelapse_test_2, name='timelapse-test'),
    path('Timelapse_test_django/passthrough/', views.timelapse_test_django_passthrough, name='timelapse-test-passthrough'),
    path('Timelapse_test_django/passthrough/wms/<str:netcdf>', views.timelapse_test_django_passthrough_wms, name='timelapse-test-passthrough-wms'),
    path('catalog/', views.thredds_catalog, name='catalog'),
    #path('thredds/', views.thredds_wms_view, name='thredds-wms'),
    path('thredds/', views.thredds_catalog, name='thredds-wms'),
    path('thredds/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('thredds/dodsC/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('thredds/dap4/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('thredds/fileServer/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('thredds/wcs/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('thredds/wms/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),

    path('login/Dashboard/', views.user_dashboard, name='user_dashboard'),
    # path('login/Userinfo/', views.userinfo, name='user_info'),
    path('login/Dashboard/get-csrf-token/', views.get_csrf_token, name='get-csrf-token'),
    path('login/Dashboard/save/', views.save_user_field, name='save-user-field'),
    path('login/Dashboard/load/', views.get_user_fields, name='get-user-fields'),
    # path('login/Dashboard/loadasync/', views.get_user_fields_async, name='get-user-fields-async'),
    # path('login/Dashboard/saveasync/', views.save_user_field_async, name='save-user-fields-async'),
    path('login/Dashboard/update/', views.update_user_field, name='update-user-fields'),
    path('login/Dashboard/delete/<int:id>', views.delete_user_field, name='delete-user-field'),
    # path('Logout/', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='user_logout'),  
    # path('Chart/', views.ChartView.as_view(), name='chart'), 
    path('login/Dashboard/field-menu/<int:field_id>/chartdata/<int:crop_id>/<int:soil_id>/', views.get_chart, name='chart-api'),
    path('login/Dashboard/monica-map/', views.thredds_wms_view, name='monica-map'),
    # Bootstrap test colors
    path('bootstrap/', views.bootstrap, name='bootstrap'),
    path('login/Dashboard/load_projectregion/', views.load_projectregion, name='load_projectregion'),
    path('login/Dashboard/load_polygon/<str:entity>/<int:polygon_id>/', views.load_polygon, name='load_polygon'),
    path('login/Dashboard/field-menu/<int:id>/', views.field_menu, name='field_menu'),
    # path('update_soil_profile_choices/', views.update_soil_profile_choices, name='update_soil_profile_choices'),
    # path('login/Dashboard/get-soil-data/<int:id>/', views.get_soil_data, name='get_soil_data'),
    
    ]
