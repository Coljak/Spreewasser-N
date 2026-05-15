from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from django.contrib.auth.views import LoginView, LogoutView
from . import views
from . import models

# template tagging
app_name = 'toolbox'


urlpatterns = [
    path('toolbox/', views.toolbox_dashboard, name='toolbox_dashboard'),
    path('toolbox/save-user-field/', views.save_user_field, name='save-user-field'),
    path('toolbox/get-user-fields/', views.get_user_fields, name='get-user-fields'),
    path('toolbox/delete-user-field/<int:id>/', views.delete_user_field, name='delete-user-field'),
    path('toolbox/field-projects-menu/<int:id>/', views.get_field_project_modal, name='field_projects_menu'),
    path('toolbox/load-toolbox-project-modal/', views.load_toolbox_project_modal, name='load_toolbox_project_modal'),
    # TODO check this- if needed and if used
    # path('toolbox/get_options/<str:parameter>/', views.get_options, name='get-options'),
    path('toolbox/save-project/', views.save_toolbox_project, name='save-project'),
    path('toolbox/load-project/<int:id>/', views.load_toolbox_project, name='load-project'),
    path('toolbox/delete-project/<int:id>/', views.delete_toolbox_project, name='delete-project'),
    # path('toolbox/load_polygon/', views.load_nuts_polygon, name='load_nuts_polygon'),
    # path('toolbox/load_polygon/<str:entity>/<int:polygon_id>/', views.load_nuts_polygon, name='load_nuts_polygon_entity'),
    path('toolbox/proxy/wms/', views.geoserver_wms, name='geoserver_wms'),
    path('toolbox/proxy/wms_sld/', views.geoserver_wms_sld, name='geoserver_wms_sld'),
    # Zalf sinks   
    path('toolbox/load_infiltration_gui/<str:user_field_id>/', views.load_infiltration_gui, name='load_infiltration_gui'),
    # path('toolbox/get_weighting_form/', views.get_weighting_forms, name='get_weighting_forms'),
    path('toolbox/filter_sinks/<str:sink_type>/', views.filter_sinks, name='filter_sinks'),
    # path('toolbox/filter_enlarged_sinks/', views.filter_enlarged_sinks, name='filter_enlarged_sinks'),
    path('toolbox/filter_waterbodies/', views.filter_waterbodies, name='filter_waterbodies'),
    path('toolbox/get_infiltration_results/', views.get_infiltration_results, name='get_infiltration_results'),   
    path('toolbox/get_injection_volume_chart/<str:waterbody_type>/<int:id>/', views.get_injection_volume_chart, name='get_injection_volume_chart'),
     # TU Berlin
    path('toolbox/mar_calculate_area/', views.mar_calculate_area, name='mar_calculate_area'),
    #### Sieker ####
    # Surface Waters
    path('toolbox/load_sieker_surface_water_gui/<int:user_field_id>/', views.load_sieker_surface_water_gui, name='sieker_surface_waters_gui'),
    path('toolbox/get_water_levels/<int:user_field_id>/', views.get_water_levels, name='get_water_levels'),
    path('toolbox/filter_sieker_surface_waters/', views.filter_sieker_surface_waters, name='filter_sieker_surface_waters'),
    path('toolbox/get_all_sieker_surface_waters/', views.get_all_sieker_surface_waters, name='get_all_sieker_surface_waters'),
    path('toolbox/get_sieker_surface_water_levels/<int:id>/', views.get_sieker_surface_water_levels, name='get_sieker_surface_water_levels'),
    path('toolbox/get_all_above_ground_catchment_areas/', views.get_all_above_ground_catchment_areas, name='get_all_above_ground_catchment_areas'),
    # Sieker sinks
    path('toolbox/load_sieker_sink_gui/<str:user_field_id>/', views.load_sieker_sink_gui, name='load_sieker_sink_gui'),
    path('toolbox/filter_sieker_sinks/', views.filter_sieker_sinks, name='filter_sieker_sinks'),
    path('toolbox/get_sieker_sink_results/', views.get_sieker_sink_results, name='get_sieker_sink_results'),
    # Sieker Gek
    path('toolbox/load_sieker_gek_gui/<str:user_field_id>/', views.load_sieker_gek_gui, name='load_sieker_gek_gui'),
    path('toolbox/get_all_sieker_geks/', views.get_all_sieker_geks, name='get_all_sieker_geks'),
    path('toolbox/filter_sieker_geks/', views.filter_sieker_geks, name='filter_sieker_gek'),
    # Wetlands
    path('toolbox/load_sieker_wetland_gui/<str:user_field_id>/', views.load_sieker_wetland_gui, name='load_sieker_wetland_gui'),
    path('toolbox/filter_sieker_wetlands/', views.filter_sieker_wetlands, name='filter_sieker_wetland'),
    path('toolbox/get_sieker_wetland_results/', views.get_sieker_wetland_results, name='get_sieker_wetland_results'),
    # Injection
    path('toolbox/load_injection_gui/', views.load_injection_gui, name='load_injection_gui' ),
    # Drainage
    path('toolbox/get_drainage_raster_legend/', views.get_drainage_raster_legend, name='get_drainage_raster_legend'),
    path('toolbox/load_sieker_drainage_gui/<int:user_field_id>/', views.load_sieker_drainage_gui, name='load_sieker_drainage_gui' ),
    path('toolbox/load_sieker_drainage_features/<int:user_field_id>/', views.load_sieker_drainage_features, name='load_sieker_drainage_features' ),

    path('toolbox/download_toolbox_results/', views.download_toolbox_results, name='download_toolbox_results'),
   
    path('toolbox/debug-lang/', views.debug_lang, name='debug_lang'),

    path('toolbox/test/', views.test_html, name='test_html'),
    path('toolbox/test_2/', views.test_html_2, name='test_html_2'),
    

]
