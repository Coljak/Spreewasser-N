# https://unidata.github.io/netcdf4-python/
import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta
import os

# dictionary of dtypes and their netCDF4 equivalents
DTYPES = {
    'int8': 'i1',
    'int16': 'i2',
    'int32': 'i4',
    'int64': 'i8',
    'uint8': 'u1',
    'uint16': 'u2',
    'uint32': 'u4',
    'uint64': 'u8',
    'float32': 'f4',
    'float64': 'f8',
    'str': 'S1'
}

def create_cf_conform_netcdf(file_name):
    """
    Function to create a netcdf file with the same dimensions and coordinates as the DWD netcdf files
    :param file_name: string, path to the netcdf file
    :return: xarray dataset with the same dimensions and coordinates as the DWD netcdf files
    """
    # open netcdf file
    dwd_path = '../../Geodaten/DWD_SpreeWasser_N/'
    new_path = '../../Geodaten/DWD_SpreeWasser_N_cf_v6/'
    if os.path.isfile(os.path.join(dwd_path, file_name)) and file_name.endswith('.nc'):
        org = nc.Dataset(os.path.join(dwd_path, file_name))
        # extract DWD parameter from all variables in the NetCDF
        vars = org.variables.keys()
        dwd_param = list(vars)[-1]
        
       # find the right netCDF4 datatype for creating a netCDF variable
        var_dtype = str(org[dwd_param][:].dtype)
        nc_type = DTYPES[var_dtype]

        # create new dataset with the same dimensions, variable and coordinates as the DWD netcdf files
        # cf stands for CF-conform, v4 for version 4
        new_file_name = file_name.replace('.nc', '_cf_v6.nc')
        fn = os.path.join(new_path, new_file_name)
        ds_new = nc.Dataset(fn, 'w', format='NETCDF4', zlib=True, complevel=9)

        # create dimensions
        time = ds_new.createDimension('time', None) # None is unlimited dimension
        lat = ds_new.createDimension('lat', org['lat'].size)
        lon = ds_new.createDimension('lon', org['lon'].size)

        # create variables for the dimensions
        times  = ds_new.createVariable('time', DTYPES[str(org['time'][:].dtype)], ('time',)) # f4 is float32, last argument is dimension tuple
        lats  = ds_new.createVariable('lat', DTYPES[str(org['lat'][:].dtype)], ('lat',))
        lons  = ds_new.createVariable('lon', DTYPES[str(org['lon'][:].dtype)], ('lon',))
        #value = ds_new.createVariable(dwd_param, nc_type, ('time', 'lat', 'lon',))
        # Create a variable with compression and chunking options optimized for access of timeseries in one point
        time_length = ds_new['time'].shape[0]
        value = ds_new.createVariable(dwd_param, nc_type, ('time', 'lat', 'lon'), zlib=True, complevel=9,  chunksizes=(time_length, 1, 1))


        # assign the values of the original netcdf file to the new netcdf file
        times[:] = org['time'][:]
        lats[:] = org['lat'][:]
        lons[:] = org['lon'][:]
        value[:] = org[dwd_param][:]

        # add attributes to dimensions
        times.units = org['time'].units
        times.calendar = 'gregorian'

        lats.units = 'degree_north'
        lats.long_name = 'latitude'
        lats.standard_name = 'latitude'
        lats.axis = 'Y'

        lons.units = 'degree_east'
        lons.long_name = 'longitude'
        lons.standard_name = 'longitude'
        lons.axis = 'X'

        
        

        # extract global and variable attributes from the original netcdf file (They only attributes are stored with the parameter variable in this case)
        value.units = org[dwd_param].units
        value.long_name = org[dwd_param].long_name
        value.standard_name = org[dwd_param].standard_name
        value.institution = org[dwd_param].institution
        value.source = org[dwd_param].source
        value.contact = org[dwd_param].contact
        value.description = org[dwd_param].description
        value.data_version = org[dwd_param].data_version   
        value.creation_date = org[dwd_param].creation_date
        value.history = org[dwd_param].history

        value.setncattr('minimum_value', np.nanmin(org[dwd_param][:]))
        value.setncattr('maximum_value', np.nanmax(org[dwd_param][:]))

        


        startdate_str = org['time'].units.split('since')[1].strip()
        startdate = datetime.strptime(startdate_str, '%Y-%m-%d %H:%M:%S')
        startdate = startdate.strftime('%Y-%m-%d %H:%M:%S') 
        
        min_lon = org['lon'][:].min()
        max_lon = org['lon'][:].max()
        min_lat = org['lat'][:].min()
        max_lat = org['lat'][:].max()


        # create all global attributes
        global_attrs ={'title': 'DWD ' + org[dwd_param].standard_name.replace('_', ' ') + ' data',
                        'Conventions': 'ACDD-1.3, CF-1.11',
                        'conventionsURL': 'http://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html',
                        'keywords': 'DWD, ' + org[dwd_param].standard_name.replace('_', ' '),
                        'keywords_vocabulary': 'GCMD Science Keywords',
                        'cdm_data_type': 'Grid',
                        'creator_name': org[dwd_param].institution,
                        'creator_email': org[dwd_param].contact,
                        'creator_url': 'www.dwd.de',
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
        }

        ds_new.setncatts(global_attrs)

        # close the new netcdf file
        org.close()
        ds_new.close()
        

        

        

    if __name__ == '__main__':
        print('main')
        dwd_path = '../../Geodaten/DWD_SpreeWasser_N/'
        file_list = os.listdir(dwd_path)
        for file_name in file_list:
            print(file_name)
            if file_name.endswith('.nc'):
                create_cf_conform_netcdf(file_name)