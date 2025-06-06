from django.shortcuts import render
from . import models
from swn import models as swn_models
from swn import forms as swn_forms
from . import forms
from .filters import SinkFilter, EnlargedSinkFilter, LakeFilter, StreamFilter

from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry, LineString
from django.contrib.gis.measure import D
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.forms.models import model_to_dict

from django.template.loader import render_to_string
from django.db import connection
from django.db.models import Max, Min, F, Q
import json, requests
from datetime import datetime

from shapely.geometry import shape as shapely_shape
from shapely.ops import nearest_points




# not in use
def get_elevations_for_line(line_geom):
    sql = """
    SELECT
      ST_Value(rast, 1, pt.geom) AS elevation,
      ST_AsText(pt.geom) AS point
    FROM (
      SELECT (ST_DumpPoints(ST_Segmentize(ST_GeomFromText(%s, 25833), 1))).geom
    ) pt,
    dem
    WHERE ST_Intersects(rast, pt.geom);
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [line_geom.wkt])
        return cursor.fetchall()


def create_default_project(user):
    """
    Create a default project for the user.
    """
    default_project = models.ToolboxProject(
        name= '',
        user=user,
    ).to_json()

    return json.dumps(default_project, default=str)


def toolbox_dashboard(request):
    user = request.user
    projectregion = swn_models.ProjectRegion.objects.first()
    geojson = json.loads(projectregion.geom.geojson) 
    project_region = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Spreewasser:N Projektregion',
            }
        }

    outline_injection = models.OutlineInjection.objects.first().geom.geojson
    outline_injection = json.loads(outline_injection)
    outline_injection = {
        "type": "Feature",
        "geometry": outline_injection,
        "properties": {
            "name": 'Spreewasser:N Injektionsbereich',
        }
    }

    outline_surface_water = models.OutlineSurfaceWater.objects.first().geom.geojson
    outline_surface_water = json.loads(outline_surface_water)
    outline_surface_water = {
        "type": "Feature",
        "geometry": outline_surface_water,
        "properties": {
            "name": 'Spreewasser:N Oberflächenwasser',
        }
    }

    outline_infiltration = models.OutlineInfiltration.objects.first().geom.geojson
    outline_infiltration = json.loads(outline_infiltration)
    outline_infiltration = {
        "type": "Feature",
        "geometry": outline_infiltration,
        "properties": {
            "name": 'Spreewasser:N Infiltrationsbereich',
        }
    }

    
    state_county_district_form = swn_forms.PolygonSelectionForm(request.POST or None)
    project_select_form = forms.ToolboxProjectSelectionForm(user=user)
    # project_select_form = forms.ToolboxProjectSelectionForm()
    project_form = forms.ToolboxProjectForm()
    project_modal_title = 'Create new project'

    default_project = create_default_project(user)

    context = {
        'project_region': project_region,
        'default_project': default_project,
        'state_county_district_form': state_county_district_form,
        'project_select_form': project_select_form,
        'project_form': project_form,
        'project_modal_title': project_modal_title,
        'outline_injection': outline_injection,
        'outline_surface_water': outline_surface_water,
        'outline_infiltration': outline_infiltration,
    }

    return render(request, 'toolbox/toolbox_three_split.html', context)




def load_infiltration_gui(request, user_field_id):
    if user_field_id == "null":
        user_field_id = None
    else:
        user_field_id = int(user_field_id)
    project_select_form = forms.ToolboxProjectSelectionForm()
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    user_field_geom = GEOSGeometry(user_field.geom)
    sinks = models.Sink4326.objects.filter(
        centroid__within=user_field.geom
    )
    enlarged_sinks = models.EnlargedSink4326.objects.filter(
        centroid__within=user_field.geom
    )
    streams = models.Stream4326.objects.filter(
        geom__within=user_field.geom
    )
    lakes = models.Lake4326.objects.filter(
        geom__within=user_field.geom
    )

    lake_form = LakeFilter(request.GET, queryset=lakes)
    stream_form = StreamFilter(request.GET, queryset=streams)
    sink_form = SinkFilter(request.GET, queryset=sinks)
    print("Queryset Sinks", sinks.count())
    enlarged_sink_form = EnlargedSinkFilter(request.GET, queryset=enlarged_sinks)

    overall_weighting = forms.OverallWeightingsForm()
    forest_weighting = forms.WeightingsForestForm()
    agriculture_weighting = forms.WeightingsAgricultureForm()
    grassland_weighting = forms.WeightingsGrasslandForm()


    html = render_to_string('toolbox/infiltration.html', {
        # 'sink_form': sink_form, 
        # 'enlarged_sink_form': enlarged_sink_form,
        'project_select_form': project_select_form,
        'sink_filter': sink_form,
        'enlarged_sink_filter': enlarged_sink_form,
        'streams_form': stream_form,
        'lakes_form': lake_form,
        'overall_weighting': overall_weighting,
        'forest_weighting': forest_weighting,
        'agriculture_weighting': agriculture_weighting,
        'grassland_weighting': grassland_weighting, 
    }, request=request) 

    return JsonResponse({'html': html})


def add_range_filter(filters, obj, field,  model_field=None):
    model_field = model_field or field
    min_val = obj.get(f'{field}_min')
    max_val = obj.get(f'{field}_max')

    if min_val is not None:
        if model_field == 'index_soil':
            min_val = float(min_val) / 100
        else:
            min_val = float(min_val)
        filters &= Q(**{f"{model_field}__gte": min_val})
    if max_val is not None:
        if model_field == 'index_soil':
            max_val = float(max_val) / 100
        else:
            max_val = float(max_val)
        filters &= Q(**{f"{model_field}__lte": max_val})

    return filters


def filter_sinks(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    sinks = models.Sink4326.objects.filter(geom__within=geom)
    filters = Q()
    filters = add_range_filter(filters, project['infiltration'], 'sink_area', 'area')
    filters = add_range_filter(filters, project['infiltration'], 'sink_volume', 'volume')
    filters = add_range_filter(filters, project['infiltration'], 'sink_depth', 'depth')
    filters = add_range_filter(filters, project['infiltration'], 'sink_index_soil', 'index_soil')
    print("Sinks", sinks.count())
    sinks = sinks.filter(filters)
    print("Sinks", sinks.count())

    
    land_use_values = project['infiltration'].get('sink_land_use', [])
    land_use_values = [int(value) for value in land_use_values if value.isdigit()]
    land_use_filter = (
        Q(landuse_1__in=land_use_values) &
        (Q(landuse_2__in=land_use_values) |
        Q(landuse_2__isnull=True)) &
        (Q(landuse_3__in=land_use_values) |
        Q(landuse_3__isnull=True))
        )
    sinks = sinks.filter(land_use_filter)
    if sinks.count() == 0:
        message = {
            'success': False, 
            'message': f'No sinks found in the search area.'
        }
        return JsonResponse({'message': message})
    else:
        print("Sinks", sinks.count())
        features = []
        for sink in sinks:
            centroid = sink.centroid
            geojson = json.loads(centroid.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": sink.id,
                "depth": round(sink.depth, 2),
                "area": round(sink.area, 2),
                "volume": round(sink.volume, 2),
                "index_soil": str(sink.index_soil * 100) + "%",
                "land_use_1": sink.landuse_1.de if sink.landuse_1 else None,
                "land_use_2": sink.landuse_2.de if sink.landuse_2 else None,
                "land_use_3": sink.landuse_3.de if sink.landuse_3 else None,

            }
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
        message = {
            'success': True, 
            'message': f'Found {sinks.count()} sinks'
        }
        
        return JsonResponse({'feature_collection': feature_collection, 'message': message})

def filter_enlarged_sinks(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    sinks = models.EnlargedSink4326.objects.filter(geom__within=geom)

    filters = Q()
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_area', 'area')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_volume', 'volume')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_depth', 'depth')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_volume_construction_barrier', 'volume_construction_barrier')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_volume_gained', 'volume_gained')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_index_soil', 'index_soil')
    sinks = sinks.filter(filters)


    land_use_values = project['infiltration'].get('enlarged_sink_land_use', [])
    land_use_values = [int(value) for value in land_use_values if value.isdigit()]
    land_use_filter = (
        Q(landuse_1__in=land_use_values) &
        (Q(landuse_2__in=land_use_values) |
        Q(landuse_2__isnull=True)) &
        (Q(landuse_3__in=land_use_values) |
        Q(landuse_3__isnull=True))&
        (Q(landuse_4__in=land_use_values) |
        Q(landuse_4__isnull=True))
        )
    sinks = sinks.filter(land_use_filter)
    features = []
    if sinks.count() == 0:
        message = {
            'success': False, 
            'message': f'No sinks found in the search area.'
        }
        return JsonResponse({'message': message})
    else:
        for sink in sinks:
            centroid = sink.centroid
            geojson = json.loads(centroid.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": sink.id,
                "depth": round(sink.depth, 2),
                "area": round(sink.area, 2),
                "volume": round(sink.volume, 2),
                "volume_construction_barrier": round(sink.volume_construction_barrier, 2),
                "volume_gained": round(sink.volume_gained, 2),
                "index_soil": str(sink.index_soil * 100) + "%",
                "land_use_1": sink.landuse_1.de if sink.landuse_1 else None,
                "land_use_2": sink.landuse_2.de if sink.landuse_2 else None,
                "land_use_3": sink.landuse_3.de if sink.landuse_3 else None,
                "land_use_4": sink.landuse_4.de if sink.landuse_3 else None,
            }
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
        message = {
            'success': True, 
            'message': f'Found {sinks.count()} sinks'
        }

        return JsonResponse({'feature_collection': feature_collection, 'message': message})

def filter_streams(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    distance = int(project['infiltration'].get('stream_distance_to_userfield', 0))
    streams = None
    if distance > 0:
        geom_25833 = user_field.geom.transform(25833, clone=True)
        
        geom_25833 = geom_25833.buffer(distance)
        buffered_4326 = geom_25833.transform(4326, clone=True)
        streams = models.Stream4326.objects.filter(geom__intersects=buffered_4326)
    else:
        streams = models.Stream4326.objects.filter(geom__intersects=geom)

    filters = Q()
    filters = add_range_filter(filters, project['infiltration'], 'stream_min_surplus_volume', 'min_surplus_volume')
    filters = add_range_filter(filters, project['infiltration'], 'stream_mean_surplus_volume', 'mean_surplus_volume')
    filters = add_range_filter(filters, project['infiltration'], 'stream_max_surplus_volume', 'max_surplus_volume')
    filters = add_range_filter(filters, project['infiltration'], 'stream_plus_days', 'plus_days')
    streams = streams.filter(filters)

    
    features = []
    print("COUNT(Streams)", streams.count())
    if streams.count() == 0:
        message = {
            'success': False, 
            'message': f'No streams found in the search area.'
        }
        return JsonResponse({'message': {'success': False, 'message': 'No streams found.'}})
    else:
        
        for stream in streams:
            geom = stream.geom
            geojson = json.loads(geom.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": stream.id,
                # "centroid": geom.centroid,
                "shape_length": stream.shape_length,
                "min_surplus_volume": stream.min_surplus_volume,
                "mean_surplus_volume": stream.mean_surplus_volume,
                "max_surplus_volume": stream.max_surplus_volume,
                "plus_days": stream.plus_days,
            }
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }

        message = {
            'success': True, 
            'message': f'Found {streams.count()} streams'
        }

        print('feature_collection:', feature_collection)
        return JsonResponse({'feature_collection': feature_collection, 'message': message})

def filter_lakes(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)

    distance = int(project['infiltration'].get('lake_distance_to_userfield', 0))
    lakes = None
    if distance > 0:
        # Transform to EPSG:25833 (meters) and add the buffer
        user_geom_25833 = user_field.geom.transform(25833, clone=True)
        buffer_25833 = user_geom_25833.buffer(distance)
        buffer_4326 = buffer_25833.transform(4326, clone=True)
        lakes = models.Lake4326.objects.filter(geom__intersects=buffer_4326)
    else:
        lakes = models.Lake4326.objects.filter(geom__intersects=geom)

    filter = Q()
    filter = add_range_filter(filter, project['infiltration'], 'lake_min_surplus', 'min_surplus_volume')
    filter = add_range_filter(filter, project['infiltration'], 'lake_mean_surplus', 'mean_surplus_volume')
    filter = add_range_filter(filter, project['infiltration'], 'lake_max_surplus', 'max_surplus_volume')
    filter = add_range_filter(filter, project['infiltration'], 'lake_plus_days', 'plus_days')
    lakes = lakes.filter(filter)

    if lakes.count() == 0:
        message = {
            'success': False, 
            'message': f'No lakes found in the search area.'
        }
        return JsonResponse({'message': {'success': False, 'message': 'No lakes found.'}})
    else:
        features = []
        for lake in lakes:
            # geom = lake.centroid
            geom = lake.geom
            # geom = GEOSGeometry(lake.geom)
            geojson = json.loads(geom.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": lake.id,
                "min_surplus_volume": int(lake.min_surplus_volume),
                "mean_surplus_volume": int(lake.mean_surplus_volume),
                "max_surplus_volume": int(lake.max_surplus_volume),
                "plus_days": lake.plus_days,
                "shape_length": int(lake.shape_length),
                "shape_area": int(lake.shape_area),
            }
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
        message = {
            'success': True, 
            'message': f'Found {lakes.count()} lakes'
        }
        print('feature_collection:', feature_collection)
        return JsonResponse({'feature_collection': feature_collection, 'message': message})

def calculate_index_for_selection(request):
    """
    Takes the selected sinks and  calculates 
    """
    if request.method == 'POST':
        try:
            project = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # get weightings from the project
        weighting_overall_usability=int(project['infiltration'].get('weighting_overall_usability', 20))/100
        weighting_soil_index=int(project['infiltration'].get('weighting_soil_index', 80))/100
        weighting_forest_field_capacity = int(project['infiltration'].get('weighting_forest_field_capacity', 33.3))/100
        weighting_forest_hydraulic_conductivity_1m= int(project['infiltration'].get('weighting_forest_hydraulic_conductivity_1m', 33.3))/100
        weighting_forest_hydraulic_conductivity_2m= int(project['infiltration'].get('weighting_forest_hydraulic_conductivity_2m', 33.3))/100
        weighting_agriculture_field_capacity = int(project['infiltration'].get('weighting_agriculture_field_capacity', 33.3))/100
        weighting_agriculture_hydromorphy = int(project['infiltration'].get('weighting_agriculture_hydromorphy', 33.3))/100
        weighting_agriculture_soil_type= int(project['infiltration'].get('weighting_agriculture_soil_type', 33.3))/100
        weighting_grassland_field_capacity = int(project['infiltration'].get('weighting_grassland_field_capacity', 25))/100
        weighting_grassland_hydromorphy = int(project['infiltration'].get('weighting_grassland_hydromorphy', 25))/100
        weighting_grassland_soil_type = int(project['infiltration'].get('weighting_grassland_soil_type', 25))/100
        weighting_grassland_soil_water_ratio=int(project['infiltration'].get('weighting_grassland_soil_water_ratio', 25))/100


        sink_ids = project['infiltration'].get('selected_sinks', [])
        sinks = models.Sink4326.objects.filter(id__in=sink_ids)
        enlarged_sink_ids = project['infiltration'].get('selected_enlarged_sinks', [])
        enlarged_sinks = models.EnlargedSink4326.objects.filter(id__in=enlarged_sink_ids)
        if sinks.count() == 0 and enlarged_sinks.count() == 0:
            return JsonResponse({'message': {'success': False, 'message': 'No sinks selected.'}})

        def calculate_indices(sinks, sinkType='sink'):
            sink_results = {}
            for sink in sinks:
                if sinkType == 'sink':
                    soil_properties = models.SinkSoilProperties.objects.filter(sink=sink).order_by('-percent_of_total_area')
                elif sinkType == 'enlarged_sink':
                    soil_properties = models.EnlargedSinkSoilProperties.objects.filter(enlarged_sink=sink).order_by('-percent_of_total_area')
                
                
                print(len(soil_properties))
                sink_results[sink.id] = {
                    'soil_profiles': []
                    }
                if len(soil_properties) > 0:
                    index_be_total = 0
                    for sp in soil_properties:
                        print(sp)
                        
                        index_1 = 0
                        index_2 = 0
                        
                        property_data = sp.soil_properties
                        bool_general = (not property_data.nitrate_contamination) and (not property_data.waterlog)
                        index_1 = bool_general * property_data.groundwater_distance.rating_index
                        print('index_1', index_1)
                        
                        
                        if property_data.agricultural_landuse.name == 'grassland': # id=1
                            index_2 = \
                                weighting_grassland_field_capacity * property_data.fieldcapacity.rating_index + \
                                weighting_grassland_hydromorphy * property_data.hydromorphy.rating_index + \
                                weighting_grassland_soil_type * property_data.soil_texture.rating_index + \
                                weighting_grassland_soil_water_ratio * property_data.wet_grassland.rating_index

                        elif property_data.agricultural_landuse.name == 'no_agricultural_use': # id=2
                            print('weighting_forest_field_capacity', weighting_forest_field_capacity)
                            index_2 = \
                                weighting_forest_field_capacity * property_data.fieldcapacity.rating_index + \
                                weighting_forest_hydraulic_conductivity_1m * property_data.hydraulic_conductivity_1m_rating + \
                                weighting_forest_hydraulic_conductivity_2m * property_data.hydraulic_conductivity_2m_rating

                        else: #id = 3, fields
                            print('weighting_agriculture_hydromorphy', weighting_agriculture_hydromorphy)
                            print('props.hydromorphy.rating_index', property_data.hydromorphy.rating_index)
                            index_2 = \
                                weighting_agriculture_field_capacity * property_data.fieldcapacity.rating_index + \
                                weighting_agriculture_hydromorphy * property_data.hydromorphy.rating_index + \
                                weighting_agriculture_soil_type * property_data.soil_texture.rating_index
                                
                        print('index_2', index_2)
                        index_be = weighting_overall_usability * index_1 + weighting_soil_index * index_2
                        sink_results[sink.id]['soil_profiles'].append({
                            'agricultural_landuse': property_data.agricultural_landuse.name,
                            'soil_profile_percentage': round(sp.percent_of_total_area, 2),
                            'groundwater_distance_rating_index': property_data.groundwater_distance.rating_index,
                            'index_1': round(index_1, 2),
                            'index_2': round(index_2, 2),
                            'index_be': round(index_be, 2),
                            })

                        index_be_total += index_be * sp.percent_of_total_area
                    sink_results[sink.id]['index_total'] = round(index_be_total, 2)

                    print('index_be_total', index_be_total)
                        
                else:
                    print('error')
            
            return sink_results


        sink_results = calculate_indices(sinks)
        enlarged_sink_results = calculate_indices(enlarged_sinks, sinkType='enlarged_sink')
        # Perform calculations here


        # Create a response dictionary with the calculated values
        response_data = {
            'message': {
                'success': True,
                'message': f'Calculated index for selected sinks.'
            },
            'sinks': sink_results,
            'enlarged_sinks': enlarged_sink_results,
        }

        return JsonResponse(response_data)

def load_nuts_polygon(request, entity, polygon_id):
    if request.method == 'GET':
        try:
            # Retrieve the polygon based on the ID
            if entity == 'states':
                polygon = swn_models.NUTS5000_N1.objects.get(id=polygon_id)
            elif entity == 'districts':
                polygon = swn_models.NUTS5000_N2.objects.get(id=polygon_id)
            elif entity == 'counties':
                polygon = swn_models.NUTS5000_N3.objects.get(id=polygon_id)
            

            geojson = json.loads(polygon.geom)

            feature = {
                "type": "Feature",
                "geometry": geojson,
                "properties": {
                    "nuts_name": polygon.nuts_name,
                }
            }
            # print('GeoJSON:', feature)
            return JsonResponse(feature)
        except:
            # Return an error response if the polygon is not found
            error_response = {
                "error": "Polygon not found."
            }
            return JsonResponse(error_response, status=404)
        
def load_toolbox_project(request, id):

    project = models.ToolboxProject.objects.get(pk=id)
    print("Toolbox Project: ", project)
    if not project:
        return JsonResponse({'message':{'success': False, 'message': 'Project not found'}})
    else:
        project_json = project.to_json()
        return JsonResponse({'message':{'success': True, 'message': f'Project {project.name} loaded'}, 'project': project_json})


def save_toolbox_project(request, project_id=None):
    print("CREATE Toolbox PROJECT\n", request.POST)
    if request.method == 'POST':
        user = request.user
        
        project_data = json.loads(request.body)
        toolbox_type = models.ToolboxType.objects.get(pk=project_data['toolboxType'])
        user_field = models.UserField.objects.get(pk=project_data['userField'])

        project = models.ToolboxProject.objects.create(
            name=project_data['name'],
            user=user,
            toolbox_type=toolbox_type,
            user_field=user_field,
            description=project_data['description']
        )
        project.save()

        return JsonResponse({
            'message': {
                'success': True, 
                'message': f'Project {project.name} saved'
                }, 
                'project_id': project.id, 
                'project_name': project.name
                })
    

@login_required
@csrf_protect
def save_user_field(request):
    print('Request:', request, request.user, request.method, request.body)
    if request.method == 'POST':

        if not request.headers.get('X-Csrftoken') == request.COOKIES.get('csrftoken'):
            
            return HttpResponseBadRequest('Invalid CSRF token')
        else:
            body = json.loads(request.body)
            name = body['name']
            geom = json.loads(body['geom'])
            geos = GEOSGeometry(body['geom'], srid=4326)
            user = request.user
            user_field = None
            if body['id']:
                # Update existing UserField
                user_field = models.UserField.objects.get(id=body['id'])
                user_field.name = name
                user_field.geom_json = geom
                user_field.geom = geos
                
                user_field.save()
            else:
                user_field = models.UserField(name=name, geom_json=geom, geom=geos, user=user)
                
                user_field.save()

            
            return JsonResponse({'name': user_field.name, 'geom_json': user_field.geom_json, 'id': user_field.id})
        
    else:
        return HttpResponseRedirect('toolbox:toolbox_dashboard')

@login_required
def get_user_fields(request):
    if request.method == "GET":
        user_fields = models.UserField.objects.filter(user=request.user)
        user_projects = models.ToolboxProject.objects.filter(user=request.user)
        ufs = []
        for user_field in user_fields:
            uf = model_to_dict(user_field, fields=['id', 'user', 'name', 'geom_json'])
            uf['user_projects'] = list(user_projects.filter(user_field=user_field).values('id', 'name', 'creation_date', 'last_modified'))
            ufs.append(uf)
        # print('user_fields:', ufs)
    return JsonResponse({'user_fields': ufs})

@login_required
def update_user_field(request, id):
    if request.method == 'POST':
        body = json.loads(request.body)
        name = body['name']
        geom = json.loads(body['geom'])
        geos = GEOSGeometry(body['geom'])
        # geos.transform(25833)
        user_field = models.UserField.objects.get(id=id)
        user_field.name = name
        user_field.geom_json = geom
        user_field.geom = geos
        user_field.save()
        
        return JsonResponse({'message': {'success': True, 'message': 'User field updated.'},'name': user_field.name, 'geom_json': user_field.geom_json, 'id': user_field.id})
    else:
        return JsonResponse({'message': {'success': False, 'message': 'An error occurred updating the user field.'}})

@login_required
# @csrf_protect
def delete_user_field(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            user_field = models.UserField.objects.get(id=id)

            if user_field.user == request.user:
                user_field.delete()
                return JsonResponse({'message': {'success': True, 'message': 'Field deleted'}})
            else:
                return JsonResponse({'message': {'success': False, 'message': 'You do not have permission to delete this field'}}, status=403)

        except models.UserField.DoesNotExist:
            return JsonResponse({'message': {'success': False, 'message': 'Field not found'}}, status=404)
    else:
        return JsonResponse({'message': {'success': False, 'message': 'Invalid request'}}, status=400)
    

#TODO needed?
def get_options(request, parameter):
    dropdown_list = []
    if parameter == 'toolbox-project':
        toolbox_projects = models.ToolboxProject.objects.filter(user=request.user)
        dropdown_list = [(project.id, project.name) for project in toolbox_projects]
    return JsonResponse({'options': dropdown_list})
        

@login_required
def get_field_project_modal(request, id):
    # user_projects = models.SwnProject.objects.filter(Q(user_field__id=id) & Q(user_field_user=request.user))
    user_projects = models.ToolboxProject.objects.filter(Q(user_field__id=id) & Q(user_field__user=request.user))
    print('user_projects:', user_projects)
    print('user_projects.values():', list(user_projects.values()))
    
    return JsonResponse({'projects': list(user_projects.values())})
    

def get_weighting_forms(request):
    if request.method == 'POST':
        project = json.loads(request.body)
        print('Project:', project)
        sinks = project['infiltration'].get('selected_sinks', [])
        enlarged_sinks = project['infiltration'].get('selected_enlarged_sinks', [])
        
        land_use_values = {}
        if len(sinks) > 0:
            sinks = [int(sink) for sink in sinks]
            queryset = models.Sink4326.objects.filter(id__in=sinks)
            land_use_values = set(
                queryset.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
            ).union(
                queryset.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
            ).union(
                queryset.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
            )
        if len(enlarged_sinks) > 0:
            enlarged_sinks = [int(sink) for sink in enlarged_sinks]
            queryset = models.EnlargedSink4326.objects.filter(id__in=sinks)
            land_use_values.union(set(
                    queryset.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
                ).union(
                    queryset.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
                ).union(
                    queryset.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
                ).union(
                    queryset.exclude(land_use_4__isnull=True).values_list('land_use_4', flat=True)
                )
            )
        
        land_use_values = list(land_use_values)

        context = {
            # 'forest_weighting': ForestWeightingFilter(),
            'forest_weighting': forms.WeightingsForestForm(),
            'agriculture_weighting': forms.WeightingsAgricultureForm(),
            'grassland_weighting': forms.WeightingsGrasslandForm(),
            'forms': {
                'grassland': False,
                'forest': False,
                'agriculture': False,
            }


        }
        # TODO weighting forms

        if 'forest_conifers' in land_use_values or 'forest_deciduous_trees' in land_use_values \
            or 'forest_conifers_and_deciduous_trees' in land_use_values:
            context['forms']['forest'] = True
        if 'agricultural_area_without_information' in land_use_values or 'farmland' in land_use_values:
            context['forms']['agriculture'] = True
        if 'grassland' in land_use_values:
            context['forms']['grassland'] = True
        

        return render(request, 'toolbox/weighting_tab.html', context)


def get_shortest_connection_lines_utm(sinks, lakes, streams):
    """
    Get the shortest connection line between the sinks and the nearest selected lake or stream.
    Returns a list of dictionaries with sink_id, waterbody_type, waterbody_id, line (WKT), and length_m.
    """
    results = []

    for sink in sinks:
        sink_geom = shapely_shape(json.loads(sink.geom25833.geojson))

        min_dist = float('inf')
        closest_geom = None
        waterbody_type = None
        waterbody_id = None

        # Check lakes
        for lake in lakes:
            lake_geom = shapely_shape(json.loads(lake.geom25833.geojson))
            dist = sink_geom.distance(lake_geom)
            if dist < min_dist:
                min_dist = dist
                closest_geom = lake_geom
                waterbody_type = 'lake'
                waterbody_id = lake.id

        # Check streams
        for stream in streams:
            stream_geom = shapely_shape(json.loads(stream.geom25833.geojson))
            dist = sink_geom.distance(stream_geom)
            if dist < min_dist:
                min_dist = dist
                closest_geom = stream_geom
                waterbody_type = 'stream'
                waterbody_id = stream.id

        # Find nearest points and build LineString in EPSG:25833
        nearest = nearest_points(sink_geom, closest_geom)
        line = LineString([nearest[0].coords[0], nearest[1].coords[0]])
        length_m = line.length  # Already in meters (EPSG:25833 is a projected CRS)

        results.append({
            'sink_id': sink.id,
            'is_enlarged_sink': sink.__class__ == models.EnlargedSink4326,
            'waterbody_type': waterbody_type,
            'waterbody_id': waterbody_id,
            'line': line.geojson,
            'length_m': round(length_m, 2),
        })

    return results

def get_elevation_profile(line_geojson):
    """
    Gets an elevation profile in a 20m raster for a given line geometry.
    Returns a list of dictionaries with {'dist': 20.0, 'nr': 1, 'x': 451082.0, 'y': 5758479.0, 'z': 60.7175178527832}.
    """
    start = datetime.datetime.now()
    url = "https://isk.geobasis-bb.de/elevation/geojson/line"  
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(line_geojson))

    if response.status_code == 200:
        elevation_data = response.json()
        return {'success': True, 'data': elevation_data}
    else:
        return {'success': False, 'error': f'Error{response.status_code}: {response.text}'}

