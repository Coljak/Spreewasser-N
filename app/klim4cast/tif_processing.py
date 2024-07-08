import rasterio
import numpy as np
from netCDF4 import Dataset
from affine import Affine
import os
from datetime import datetime
# import CRS


# TODO: UTCI:Check what the scale is! units: degree_C or K??? --> https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html


KEYWORD_VOCABULARY = {
    
    'AWD_0-40cm': { # Average Water Deficit maybe??? TODO: find CF standard name
        'standard_name': 'Soil Moisture Deficit',
        'description': 'Soil Moisture Deficit in the soil layer 0-40cm',
        'long_name': 'Soil Moisture Deficit',
        'units': 'mm',
    },
    'AWD_0-100cm': { # Average Water Deficit maybe??? TODO: find CF standard name
        'standard_name': 'Soil Moisture Deficit',
        'description': 'Soil Moisture Deficit in the soil layer 0-100cm',
        'long_name': 'Soil Moisture Deficit',
        'units': 'mm',
    },
    'AWD_0-200cm': { # Average Water Deficit maybe??? TODO: find CF standard name
        'standard_name': 'Soil Moisture Deficit',
        'description': 'Soil Moisture Deficit in the soil layer 0-200cm',
        'long_name': 'Soil Moisture Deficit',
        'units': 'mm',
    },
    'AWP_0-40cm': {
        'standard_name': 'Intensity of Drought',
        'description': 'Intensity of Drought in the soil layer 0-40cm',
        'long_name': 'Intensity of Drought',
        'units': '%',
    },
    'AWP_0-100cm': {
        'standard_name': 'Intensity of Drought',
        'description': 'Intensity of Drought in the soil layer 0-100cm',
        'long_name': 'Intensity of Drought',
        'units': '%',
    },
    'AWP_0-200cm': {
        'standard_name': 'Intensity of Drought',
        'description': 'Intensity of Drought in the soil layer 0-200cm',
        'long_name': 'Intensity of Drought',
        'units': '%',
    },
    'AWR_0-40cm': {
        'standard_name': 'Relative Soil Saturation',
        'description': 'Relative Soil Saturation in the soil layer 0-40cm',
        'long_name': 'Relative Soil Saturation',
        'units': '%',
        'min': 0.0,
        'max': 100.0,
    },
    'AWR_0-100cm': {
        'standard_name': 'Relative Soil Saturation',
        'description': 'Relative Soil Saturation in the soil layer 0-100cm',
        'long_name': 'Relative Soil Saturation',
        'units': '%',
        'min': 0.0,
        'max': 100.0,
    },
    'AWR_0-200cm': {
        'standard_name': 'Relative Soil Saturation',
        'description': 'Relative Soil Saturation in the soil layer 0-200cm',
        'long_name': 'Relative Soil Saturation',
        'units': '%',
        'min': 0.0,
        'max': 100.0,
    },
    'DFM10H': { # TODO: Check if this is the correct standard name, 10 hours are not in the cf list
        'standard_name': 'ndfrs_10_hour_dead_fuel_moisture',
        'long_name': 'Dead Fuel Moisture',
        'description': 'Dead Fuel Moisture 10 hours',
        'units': '%',
        'min': 0.0,
        'max': 35.0,
    },
    'FWI_GenZ': { # TODO: Check if this is the correct standard name, is it Canadian fire weather index? 
        'standard_name': 'Fire Weather Index',
        'long_name': 'Fire Weather Index',
        'description': 'Fire Weather Index- Fire Spread',
        'units': '1',
        'min': 1.0,
        'max': 6.0,
        'nodata': 15,
    },
    'HI': { # TODO: is it heat_index_of_air_temperature? Check if this is the correct standard name It would be K
        'standard_name': 'Heat Index',
        'long_name': 'Heat Index',
        'description': 'Heat Index in °C',
        'units': 'degree_C',
        'min': 0.0,
        'max': 50.0,
    },
    'UTCI': {
        'standard_name': 'universal_thermal_climate_index',
        'long_name': 'Universal Thermal Comfort Climate Index',
        'description': 'Universal Thermal Comfort Climate Index in °C',
        'units': 'degree_C',
        'min': -50.0,
        'max': 50.0,
        'extra': {
            'cold_stress': 'below 0',
            'heat_stress': 'above 26',
            
        }
    },

}

def load_tif_stacks(input_dir):
    """
    A dictionary is created from all downloaded .tif files in the input directory.
    The dictionary contains metadata and data.
    """
    tif_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]
    tif_files.sort()
    input_name = ''
    path_dict = {
        'meta': None,
    }
    
    for tif_name in tif_files:

        name_parts = tif_name.split('.tif')[0].split('_')
        iso_date = name_parts[-1]
        name_parts.pop(-1)

        if len(name_parts) > 1:
            name = '_'.join(name_parts)
        else:
            name = name_parts[0]

        if input_name != name:
            input_name = name
            path_dict[name] = {
                'dates': [],
                'standard_name': name_parts[0],
                'tif_meta': None,
                'upper_limit': None,
                'lower_limit': None,
                'data': [],
                'paths': []
            }

            if len(name_parts) > 1:
                try:
                    path_dict[name]['upper_limit'] = int(name_parts[-1].split('cm')[0].split('-')[0])
                    path_dict[name]['lower_limit'] = int(name_parts[-1].split('cm')[0].split('-')[1])
                except:
                    pass               

        with rasterio.open(os.path.join(input_dir, tif_name)) as src:
            path_dict[name]['tif_meta'] = src.meta
            path_dict[name]['data'].append(src.read(1))

        path_dict[name]['dates'].append(iso_date)
        path_dict[name]['paths'].append(os.path.join(input_dir, tif_name))

    
    for k, v in path_dict.items():
        # print('KEY:', k, 'VALUE:', v)
        if k == 'meta':
            print('Checked variable ', k)
            continue
        elif path_dict['meta'] is None:  
            path_dict['meta'] = {
                'height': v['tif_meta']['height'],
                'width': v['tif_meta']['width'],
                'transform': v['tif_meta']['transform'],
                'crs': v['tif_meta']['crs'],
                'dates': v['dates']
            }      
            print('Elif: Checked variable ', k, 'with dates:', v['dates'])
        else:
            if path_dict['meta']['width'] != v['tif_meta']['width']:
                raise ValueError('Width of .tif files  in variable ' + k + 'does not match previous width!')
            if path_dict['meta']['height'] != v['tif_meta']['height']:
                raise ValueError('Height of .tif files in variable ' + k + 'does not match previous height!')
            if path_dict['meta']['transform'] != v['tif_meta']['transform']:
                raise ValueError('Transform of .tif files in variable ' + k + 'does not match previous transform!')
            if path_dict['meta']['crs'] != v['tif_meta']['crs']:
                raise ValueError('CRS of .tif files in variable ' + k + 'does not match previous CRS!')
            if path_dict['meta']['dates'] != path_dict[k]['dates']:

                raise ValueError('Dates of .tif files do not match in variable ' + k + ': 1. ' + str(path_dict['meta']['dates']) + ', 2. ' + str(path_dict[k]['dates']))
            print('Else: Checked variable ', k, 'with dates:', v['dates'])

    return path_dict


def create_netcdf(path_dict, output_dir='./data/nc_files/'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print('Checkpoint 1')
    dates = path_dict['AWD_0-40cm']['dates']
    print('Checkpoint 2')
    file_name = 'ChechGlobe_' + dates[0] + '-' + dates[-1] + '.nc'
    print('Checkpoint 3')
    netcdf_file_path = os.path.join(output_dir, file_name)
    print('Checkpoint 4')
    with Dataset(netcdf_file_path, 'w', format='NETCDF4') as dst:
        time = dst.createDimension('time', None) # unlimited dimension, but actually len(dates)
        lat = dst.createDimension('lat', path_dict['meta']['height'])
        lon = dst.createDimension('lon', path_dict['meta']['width'])
        
        times = dst.createVariable('time', 'i2', ('time',))
        latitudes = dst.createVariable('lat', 'f4', ('lat',))
        longitudes = dst.createVariable('lon', 'f4', ('lon',))      

        times[:] = np.arange(len(dates))
        times.units = f'days since {dates[0]} 00:00:00'
        times.calendar = 'gregorian'

        start_lon = path_dict['meta']['transform'][2]
        lon_step = path_dict['meta']['transform'][0]
        start_lon = start_lon + lon_step/2
        lon_len = path_dict['meta']['width']

        start_lat = path_dict['meta']['transform'][5]
        lat_step  = path_dict['meta']['transform'][4]
        start_lat = start_lat + lat_step/2
        lat_len = path_dict['meta']['height']

        lons = np.array([start_lon + i * lon_step for i in range(lon_len)])
        lats = np.array([start_lat + i * lat_step for i in range(lat_len)])

        latitudes[:] = lats[:]
        longitudes[:] = lons[:]
        
        latitudes.units = 'degree_north'
        latitudes.long_name = 'latitude'
        latitudes.standard_name = 'latitude'
        latitudes.axis = 'Y'

        longitudes.units = 'degree_east'
        longitudes.long_name = 'longitude'
        longitudes.standard_name = 'longitude'
        longitudes.axis = 'X'

            
        dst.setncattr('dates', dates)

        dst.setncattr('history', 'Created ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        min_lat = lats.min()
        max_lat = lats.max()
        min_lon = lons.min()
        max_lon = lons.max()

        title = 'ChechGlobe Klim4Cast ' + dates[0] + ' to ' + dates[-1]
        keywords = ', '.join(set([v['standard_name'] for k,v in KEYWORD_VOCABULARY.items()]))
        
        startdate = datetime.strptime(dates[0], '%Y-%m-%d')
        startdate = startdate.strftime('%Y-%m-%d %H:%M:%S') 
        global_attrs ={'title': title,
                    'institution': 'ChechGlobe',
                        'Conventions': 'ACDD-1.3, CF-1.11',
                        'conventionsURL': 'http://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html',
                        'keywords': 'ChechGlobe, ' + keywords,
                        'keywords_vocabulary': 'GCMD Science Keywords', #TODO: not really true!!
                        'cdm_data_type': 'Grid',
                        # 'creator_name': org[dwd_param].institution,
                        # 'creator_email': org[dwd_param].contact,
                        'creator_url': 'www.czechglobe.cz',
                        'publisher_name': 'Zentrum für Agrarlandschaftsforschung (ZALF) e.V.',
                        'publisher_email': 'colja.krugmann@zalf.de',
                        'publisher_url': 'www.zalf.de',
                        'date_metadata_modified': datetime.now().strftime('%Y-%m-%d'),
                        'geospatial_bounds': 'POLYGON (({} {}, {} {}, {} {}, {} {}))'.format(
                            min_lon, min_lat, max_lon, min_lat, max_lon, max_lat, min_lon, max_lat
                        ),
                        'geospatial_bounds_crs': 'EPSG:4326',
                        'geospatial_lat_min': str(min_lat),
                        'geospatial_lat_max': str(max_lat),
                        'geospatial_lon_min': str(min_lon),
                        'geospatial_lon_max': str(max_lon),
                        'time_coverage_start': startdate + 'A', # Timezone UTC+100
                        # 'time_coverage_end': str(org['time'][:].max()) + 'A', # Timezone UTC+100, A. 
                        'time_coverage_resolution': 'P1D',
                        'comment': 'NetCDF created from .tif files generated by ChechGlobe',
        }
        print('Checkpoint 5')
        dst.setncatts(global_attrs)
        print('Checkpoint 6')
        for name, data in path_dict.items():
            if name != 'meta':
                variable = dst.createVariable(name, 'f4', ('time', 'lat', 'lon'), fill_value=data['tif_meta']['nodata'])

                width = data['tif_meta']['width']
                height = data['tif_meta']['height']
                dates = data['dates']
                time_length = len(dates)  

                variable[:] = np.array(data['data'])

                variable.units = KEYWORD_VOCABULARY[name]['units']
                variable.long_name = KEYWORD_VOCABULARY[name]['long_name']
                variable.standard_name = KEYWORD_VOCABULARY[name]['standard_name']
                variable.description = KEYWORD_VOCABULARY[name]['description']
                variable.setncattr('minimum_value', np.nanmin(variable[:]))
                variable.setncattr('maximum_value', np.nanmax(variable[:]))
                variable.setncattr('nodata', data['tif_meta']['nodata'])
                if data['upper_limit'] is not None:
                    variable.setncattr('upper_limit', data['upper_limit'])
                    variable.setncattr('lower_limit', data['lower_limit'])

        print('Checkpoint 7')


def process_tifs(input_dir, output_dir):
    try:
        path_dict = load_tif_stacks(input_dir)
        create_netcdf(path_dict, output_dir)

        return "NetCDF file created successfully!"
    except Exception as e:
        return f"Error: NetCDF could not be created. {e}"

            

            