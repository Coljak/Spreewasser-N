from django.urls import path

from . import views

urlpatterns = [
    path('api/schema/', views.api_schema, name='api_schema'),
    # path('api/original_soil_data/<str:lat>/<str:lon>/', views.get_buek_polygon_id_from_point_buek200, name='original_soil_data'),
    path('api/soil_data/<str:lat>/<str:lon>/', views.get_buek_data_from_point, name='soil_data'),
    path('api/soil_profile/<str:profile_type>/<str:lat>/<str:lon>/', views.get_soil_profile_from_point, name='soil_profile'),
    path('api/original_buek200/<str:lat>/<str:lon>/', views.get_profiles_from_point_buek200, name='original_buek200'),
    path('test_split/', views.test_split, name='test_split'),
]

