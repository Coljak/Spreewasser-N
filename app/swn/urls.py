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
    # general paths
    path('', views.IndexView.as_view(), name='swn_index'),
    path('', include('django.contrib.auth.urls')),
    path('favicon.ico', views.favicon_view, name='favicon'),
    #user related paths
    path('sign-up/', views.sign_up, name='sign_up'),
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
    path('login/Dashboard/field-edit/<int:id>/', views.field_edit, name='field_edit'),
    path('login/Dashboard/field-edit/<int:field_id>/chartdata/<int:crop_id>/<int:soil_id>/', views.get_chart, name='chart-api'),
    path('login/Dashboard/monica-map/', views.thredds_wms_view, name='monica-map'),
    # Impressum and Acknoledgements
    path('Impressum-Information/', views.ImpressumView.as_view(), name='impressum_information'),
    path('acknoledgements/', views.AcknoledgementsView.as_view(), name='acknoledgements'),
    # Thredds timelapse paths
    # test can be deleted - it is a direct access from the browser to the thredds server 
    path('Timelapse_test/', views.timelapse_test, name='timelapse-test'),
    # Thredds Timelapse page, metadata and capabilities
    path('Timelapse/', views.timelapse_items, name='timelapse-page'),
    path('Thredds/get_ncml_metadata/<str:name>', views.get_ncml_metadata, name='get-ncml-metadata'),
    path('Thredds/get_wms_capabilities/<str:name>', views.get_wms_capabilities, name='get-wms-capabilities'),
    path('Thredds/wms/<str:netcdf>', views.timelapse_test_django_passthrough_wms, name='timelapse-test-passthrough-wms'),
    path('Thredds/catalog/', views.thredds_catalog, name='thredds-catalog'),
    path('Thredds/wms/timeseries/', views.get_timeseries_data, name='get-timeseries-data'),
    # path('Thredds/catalog/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/dodsC/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/dap4/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/fileServer/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/wcs/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/wms/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    path('bootstrap/', views.bootstrap, name='bootstrap'),
    path('login/Dashboard/load_projectregion/', views.load_projectregion, name='load_projectregion'),
    path('login/Dashboard/load_polygon/<str:entity>/<int:polygon_id>/', views.load_polygon, name='load_polygon'),
    
    # path('update_soil_profile_choices/', views.update_soil_profile_choices, name='update_soil_profile_choices'),
    # path('login/Dashboard/get-soil-data/<int:id>/', views.get_soil_data, name='get_soil_data'),
    
    ]
