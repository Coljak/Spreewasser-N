from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
import requests
import xmltodict
from datetime import datetime, timedelta

def klim4cast(request):
    return 'Klim4Cast'

def klim4cast_timelapse_items(request):
    # List of datasaet as in the thredds_catalog view
    url = 'http://thredds:8080/thredds/catalog/data/Klim4Cast/catalog.xml'

    response = requests.get(url)
    catalog_dict = xmltodict.parse(response.content)
    print("\nKlim4Cast catalog_dict['catalog']['dataset']['dataset']\n", catalog_dict['catalog']['dataset']['dataset'], type(catalog_dict['catalog']['dataset']['dataset']))
    print('TYPE is list:', type(catalog_dict['catalog']['dataset']['dataset']) == 'list')
    # thredds content as dataset from list comprehension
    if isinstance(catalog_dict['catalog']['dataset']['dataset'], list):
        catalog_dict_list = [
            {
                "name": dataset['@name'].split('.nc')[0],
                "urlPath": dataset['@urlPath'],
                "size": f"{dataset['dataSize']['#text']} {dataset['dataSize']['@units']}",
                "date_modified": (
                    datetime.strptime(dataset['date']['#text'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if '.' in dataset['date']['#text']
                    else datetime.strptime(dataset['date']['#text'], "%Y-%m-%dT%H:%M:%SZ")
                ).strftime("%d-%m-%Y"),
            }
            for dataset in catalog_dict['catalog']['dataset']['dataset']
        ]
    else:
        catalog_dict_list = [
            {
                "name": catalog_dict['catalog']['dataset']['dataset']['@name'],
                "urlPath": catalog_dict['catalog']['dataset']['dataset']['@urlPath'],
                "size": f"{catalog_dict['catalog']['dataset']['dataset']['dataSize']['#text']} {catalog_dict['catalog']['dataset']['dataset']['dataSize']['@units']}",
                "date_modified": (
                    datetime.strptime(catalog_dict['catalog']['dataset']['dataset']['date']['#text'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if '.' in catalog_dict['catalog']['dataset']['dataset']['date']['#text']
                    else datetime.strptime(catalog_dict['catalog']['dataset']['dataset']['date']['#text'], "%Y-%m-%dT%H:%M:%SZ")
                ).strftime("%d-%m-%Y"),
            }
        ]

    return render(request, 'klim4cast/klim4cast.html', {'catalog_json': catalog_dict_list, 'thredds_data': 'thredds_data'})


def get_ncml_metadata(request, name):
    url = "http://thredds:8080/thredds/ncml/data/Klim4Cast/" + name + '.nc'
    nc_dict = {}
    ncml = requests.get(url)
    ncml_data = xmltodict.parse(ncml.text)
    try:
        nc_dict['global_attributes'] = {}
        for attr in ncml_data['netcdf']['attribute']:
            nc_dict['global_attributes'][attr['@name']] = attr['@value']

        nc_dict['dimensions'] = {}
        for var in ncml_data['netcdf']['dimension']:
            nc_dict['dimensions'][var['@name']] = {'length': var['@length']}
            if '@isUnlimited' in var.keys():
                nc_dict['dimensions'][var['@name']]['isUnlimited'] = var['@isUnlimited']

        nc_dict['variables'] = {}
        for var in ncml_data['netcdf']['variable']:
            print('var', var)
            if var['@name'] not in ['latitude', 'lat', 'longitude', 'lon', 'long', 'time']:
                nc_dict['variables'][var['@name']] = {'shape': var['@shape'], 'type': var['@type'], 'attributes': {}}
                for att in var['attribute']:
                    attribute_name = att['@name']
                    attribute_value = att.get('@value', '')  # Use .get to provide a default empty string
                    print(f"Processing attribute {attribute_name} with value {attribute_value}")
                    # Ensure attribute_value is a string
                    if isinstance(attribute_value, str):
                        nc_dict['variables'][var['@name']]['attributes'][attribute_name] = attribute_value.encode('utf-8').decode('utf-8')
                    else:
                        nc_dict['variables'][var['@name']]['attributes'][attribute_name] = str(attribute_value)
    except Exception as e:
        print(f"Error processing NCML metadata: {e}")
        nc_dict = {'error': 'No metadata available'}

    data = {}
    data['title'] = nc_dict['global_attributes']['title']
    data['variable'] = [x for x in list(nc_dict['variables'].keys()) if x not in list(nc_dict['dimensions'].keys())]
    time_coverage_start = nc_dict['global_attributes']['time_coverage_start']
    
    start_date = datetime.strptime(time_coverage_start, "%Y-%m-%d %H:%M:%SA")
    time_coverage_start = start_date.strftime("%Y-%m-%d")
    data['time_coverage_start'] = time_coverage_start
    new_date = start_date + timedelta(days=int(nc_dict['dimensions']['time']['length']))
    data['time_coverage_end'] = new_date.strftime("%Y-%m-%d")
    nc_dict['global_attributes']['time_coverage_start_ymd'] = time_coverage_start
    nc_dict['global_attributes']['time_coverage_end_ymd'] = new_date.strftime("%Y-%m-%d")

    # print('data', data)         
    print('NC Dict:', nc_dict)

    return JsonResponse(nc_dict)


def timelapse_django_passthrough_wms(request, netcdf):
    """
    Incoming requests are passed through to the Thredds server.
    """
    netcdf += '.nc'
    print("klim4cast.views.timelapse_django_passthrough_wms", netcdf)
    url = 'http://thredds:8080/thredds/wms/data/Klim4Cast/' + netcdf
    
    params = request.GET.dict()
    # Timeseries legend image
    
    # Timeseries WMS
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print("response.headers['Content-Type']", response.headers['Content-Type'])
        # Return the response content to the frontend
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        # Handle request exception, e.g., log the error
        print(f"Error: {e}")
        return HttpResponse(f"Error: {e}", content_type='text/plain')