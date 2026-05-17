from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
import requests
import xmltodict
import xarray as xr
import numpy as np
from datetime import datetime, timedelta, date
import json
from django.conf import settings
import os


def klim4cast_timelapse_items(request):
    # List of datasaet as in the thredds_catalog view

    netcdfs = os.listdir(settings.CLIM4CAST_NETCDF_DIR)
    netcdfs = [f.split('.nc')[0] for f in netcdfs if f.endswith('.nc')]


    return render(request, 'klim4cast/klim4cast.html', {'netcdfs': netcdfs})



def get_ncml_metadata(request, name):

    data = {'variables': {}}

    with xr.open_dataset(
        f"{settings.CLIM4CAST_NETCDF_DIR}/{name}.nc",
        decode_times=False
    ) as ds:

        for var_name, da in ds.data_vars.items():

            data['variables'][var_name] = {
                'attributes': dict(da.attrs),
                # 'shape': da.shape,
                # 'dtype': str(da.dtype),
                # 'dims': da.dims,
            }

            for attr_name, attr_value in da.attrs.items():
                if isinstance(attr_value, bytes):
                    data['variables'][var_name]['attributes'][attr_name] = attr_value.decode('utf-8')
                else:
                    data['variables'][var_name]['attributes'][attr_name] = str(attr_value)
        data['title'] = ds.attrs['title']

        data['time_coverage_start'] = (
            ds.attrs['time_coverage_start'].split(' ')[0]
        )

        start_date = datetime.strptime(
            ds.attrs['time_coverage_start'],
            "%Y-%m-%d %H:%M:%SA"
        )

        new_date = start_date + timedelta(
            days=int(ds.sizes['time'])
        )

        data['time_coverage_end'] = (
            new_date.strftime("%Y-%m-%d")
        )

        data['time_coverage_start_ymd'] = (
            data['time_coverage_start']
        )

        data['time_coverage_end_ymd'] = (
            new_date.strftime("%Y-%m-%d")
        )
    print(data)
    return JsonResponse(data)



def timelapse_django_passthrough_wms(request, netcdf):
    """
    Incoming requests are passed through to the Thredds server.
    """
    netcdf += '.nc'
    print("klim4cast.views.timelapse_django_passthrough_wms", netcdf)
    url = f"{settings.THREDDS_URL}/wms/data/Klim4Cast/{netcdf}"
    
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
    

def get_point_data(request):
    """
    Incoming requests are passed through to the Thredds server.
    """
    print('check 1 - get_point_data called with method:', request.method)
    if request.method == 'POST':
        data = json.loads(request.body)

        netcdf = f"{data.get('netcdf', '')}.nc"
        param = data.get('param', '')
        lat = data.get('lat', '')
        lon = data.get('lon', '')

        print("klim4cast.views.get_point_data", netcdf, param, lat, lon)

        with xr.open_dataset(f"{settings.CLIM4CAST_NETCDF_DIR}/{netcdf}") as ds:
            point_data = ds[param].sel(lat=lat, lon=lon, method='nearest').values
            dates = ds['time'].dt.strftime('%Y-%m-%d').values.tolist()
            long_name = ds.data_vars[param].long_name if 'long_name' in ds.data_vars[param].attrs else param
            unit = ds.data_vars[param].units if 'units' in ds.data_vars[param].attrs else ''

        return JsonResponse({
            'point_data': point_data.tolist(),
            'dates': dates,
            'long_name': long_name,
            'unit': unit,
            'latitude': lat,
            'longitude': lon,
        })
    

# def get_data(request, name, variable, lat, lon):
#     """
#     Get data from the Thredds server.
#     """
#     path = f"{settings.CLIM4CAST_NETCDF_DIR}/{name}.nc"
#     nc = xr.open_dataset(path)

#     lat = float(lat)
#     lon = float(lon)

#     ds = nc.sel(lat=lat, lon=lon, method='nearest')

#     context = {
#         'variable': variable,
#         'long_name': ds.data_vars[variable].long_name,
#         'dates': [str(date)[:10] for date in ds.time.values],  # Convert datetime64 to string
#         'values': [float(val) for val in ds.data_vars[variable].values.flatten()],  # Convert NumPy types to Python
#         'latitude': lat,
#         'longitude': lon,
#     }

#     try:
#         context['unit'] = ds.data_vars[variable].units
#     except AttributeError:
#         context['unit'] = ''

#     try:
#         context['upper_limit'] = float(ds.data_vars[variable].upper_limit) if np.isscalar(ds.data_vars[variable].upper_limit) else ''
#         context['lower_limit'] = float(ds.data_vars[variable].lower_limit) if np.isscalar(ds.data_vars[variable].lower_limit) else ''
#     except AttributeError:
#         context['upper_limit'] = ''
#         context['lower_limit'] = ''

#     print('context', context)
#     return JsonResponse(context)
