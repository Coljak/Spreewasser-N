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
    # path('drought/', views.user_dashboard, name='user_dashboard'),
    path('drought/', views.three_split, name='swn_user_dashboard'),
    path('drought/get-csrf-token/', views.get_csrf_token, name='get-csrf-token'),
    path('drought/save-user-field/', views.save_user_field, name='save-user-field'),
    path('drought/load-user-field/', views.get_user_fields, name='get-user-fields'),
    path('drought/update-user-field/', views.update_user_field, name='update-user-field'),
    path('drought/delete-user-field/<int:id>', views.delete_user_field, name='delete-user-field'),
    # path('drought/create-project/', views.create_project, name='create-project'),
    path('drought/save-project/', views.save_swn_project, name='save-project'),

    path('drought/load-project/<int:id>/', views.load_swn_project, name='load-project'),
    path('drought/get_options/<str:parameter_type>/', views.get_parameter_options, name='get_parameter_options'),
    path('drought/get_options/<str:parameter_type>/<int:id>/', views.get_parameter_options, name='get_parameter_options'),
    # path('drought/field-edit/<int:id>/', views.field_edit, name='field_edit'),
    path('drought/field-projects-menu/<int:id>/', views.get_field_project_modal, name='field_projects_menu'),
    # path('drought/get_lat_lon/<int:user_field_id>/', views.get_centroid, name='get_centroid'),
    path('drought/manual-soil-selection/<int:user_field_id>/', views.manual_soil_selection, name='manual_soil_selection'),
    path('drought/recommended-soil-profile/<str:profile_landusage>/<int:user_field_id>/', views.recommended_soil_profile, name='recommended_soil_profile'),
    path('drought/run-simulation/', views.run_simulation, name='run_simulation'),
    
    # path('login/Dashboard/field-edit/<int:field_id>/chartdata/<int:crop_id>/<int:soil_id>/', views.get_chart, name='chart-api'),
    # Impressum and Acknoledgements
    path('Impressum-Information/', views.ImpressumView.as_view(), name='impressum_information'),
    path('acknoledgements/', views.AcknoledgementsView.as_view(), name='acknoledgements'),
    # Thredds timelapse paths
    # Thredds Timelapse page, metadata and capabilities
    path('Timelapse/', views.timelapse_items, name='timelapse-page'),
    path('Thredds/get_ncml_metadata/<str:name>', views.get_ncml_metadata, name='get-ncml-metadata'),
    path('Thredds/get_wms_capabilities/<str:name>', views.get_wms_capabilities, name='get-wms-capabilities'),
    path('Thredds/wms/<str:netcdf>', views.timelapse_test_django_passthrough_wms, name='timelapse-test-passthrough-wms'),
    path('Thredds/catalog/', views.thredds_catalog, name='thredds-catalog'),
    # path('Thredds/wms/timeseries/', views.get_timeseries_data, name='get-timeseries-data'),
    ## --the folloeing URLs are  renderings of the thredds Gui using  scraping --##
    # path('Thredds/catalog/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/dodsC/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/dap4/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/fileServer/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/wcs/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    # path('Thredds/wms/<path:thredds_link>', views.thredds_wms_view, name='thredds-wms'),
    path('bootstrap/', views.bootstrap, name='bootstrap'),
    path('drought/load_polygon/', views.load_nuts_polygon, name='load_nuts_polygon'),
    path('drought/load_polygon/<str:entity>/<int:polygon_id>/', views.load_nuts_polygon, name='load_nuts_polygon_entity'),

    ]

