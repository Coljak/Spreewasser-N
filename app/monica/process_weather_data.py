import xarray as xr
import numpy as np
from datetime import datetime
from .models import WeatherData
# from django.contrib.gis.geos import Point
import os
import pandas as pd
import json
import concurrent.futures

# from monica.climate_data.lat_lon_mask  import lat_lon_mask 

def create_path_list_dict():
    """
    This function creates a dictionary of all weather data. 
    dir_paths_dict = {
        '2011': ['/app/thredds_data/DWD_Data/zalf_hurs_amber_2021_v1-0_cf_v6.nc.nc', ...],
    """
    dir_list = os.listdir('/app/thredds_data/DWD_Data/')
    dir_list.sort()
    dir_paths_dict = {}
    for dir in dir_list:
        year = dir.split('_')[3]
        dir_paths_dict[year] = []
    for dir in dir_list:
        year = dir.split('_')[3]
        dir_paths_dict[year].append('/app/thredds_data/DWD_Data/' + dir)
        
    return dir_paths_dict

def create_composed_netcdf(year):
    try:
        year = str(year)
    except:
        pass

    return xr.open_mfdataset(create_path_list_dict()[year], combine='by_coords')

# rather obsolete
def import_weather_data_to_db(year):
    # Load NetCDF file using xarray
    ds = create_composed_netcdf(year)

    # Extract coordinates and data variables
    times = ds['time'].values
    lats = ds['lat'].values
    lons = ds['lon'].values

    # Iterate over time, latitude, and longitude
    for t_idx, time in enumerate(times):
        for lat_idx, lat in enumerate(lats):
            for lon_idx, lon in enumerate(lons):
                # Extract data variables for the current time, lat, lon
                date = pd.Timestamp(time).date()
                tas = ds['tas'][t_idx, lat_idx, lon_idx].values
                tasmin = ds['tasmin'][t_idx, lat_idx, lon_idx].values
                tasmax = ds['tasmax'][t_idx, lat_idx, lon_idx].values
                sfcwind = ds['sfcWind'][t_idx, lat_idx, lon_idx].values
                rsds = ds['rsds'][t_idx, lat_idx, lon_idx].values
                pr = ds['pr'][t_idx, lat_idx, lon_idx].values
                hurs = ds['hurs'][t_idx, lat_idx, lon_idx].values

                # Create a Point object with lat and lon
                point = Point(lon, lat)

                # Create a WeatherData instance
                weather_data = WeatherData(
                    point=point,
                    lat=lat,
                    lon=lon,
                    date=date,
                    tas=tas,
                    tasmin=tasmin,
                    tasmax=tasmax,
                    sfcwind=sfcwind,
                    rsds=rsds,
                    pr=pr,
                    hurs=hurs
                )

                # Save WeatherData instance to the database
                weather_data.save()

    # Close the NetCDF dataset
    ds.close()


def create_weather_data_json_per_point_and_year(year):
    start = datetime.now()

    # Open the NetCDF file
    ds = create_composed_netcdf(year)
    variable_names = ['tas', 'tasmin', 'tasmax', 'sfcWind', 'rsds', 'pr', 'hurs']
    # with open('/app/monica/climate_data/lat_lon_mask.json') as f:
    #     lat_lon_mask = json.load(f)

    # # for TESTPURPOSES::
    # lat_lon_mask['lat_idx'] = [200]
    # lat_lon_mask['lon_idx'] = [200]

    # for lat_idx in lat_lon_mask['lat_idx']:
    #     lat_path = f'/app/monica/climate_data/{lat_idx}'
    #     try:
    #         if not os.path.exists(lat_path):
    #             os.makedirs(lat_path)   
    #     except OSError as e:
    #         # Handle folder creation error
    #         return f"Error creating folder: {str(e)}"

    #     for lon_idx in lat_lon_mask['lon_idx']:
    #         if lat_lon_mask['mask'][lat_idx][lon_idx] == True:
                
    #             lon_path = lat_path + f'/{lon_idx}'
    #             try:
    #                 if not os.path.exists(lon_path):
    #                     os.makedirs(lon_path)

    #                 point_data = ds.sel(lat=lat_lon_mask['lat'][lat_idx], lon=lat_lon_mask['lon'][lon_idx], method='nearest')
    #                 """
    #                 The monica enum AvailableClimateData has the keys: 3: tmin (tasmin), 4: tavg (tas),
    #                 5: tmax (tasmax), 6: precip (pr),  8: globrad (rsds), 9: wind (sfcWind), 12: relhumid
    #                 """
                    
    #                 point_json = {
    #                     '3': point_data['tasmin'].values.tolist(),
    #                     '4': point_data['tas'].values.tolist(),
    #                     '5': point_data['tasmax'].values.tolist(),
    #                     '6': point_data['pr'].values.tolist(),
    #                     '8': point_data['rsds'].values.tolist(),
    #                     '9': point_data['sfcWind'].values.tolist(),
    #                     '12': point_data['hurs'].values.tolist()

    #                 }

    #                 file_path = lon_path + '/' + str(year) + '.json'

    #                 print("filepath", file_path)
    #                 with open(file_path, 'w') as f:
    #                     json.dump(point_json, f)
    #             except OSError as e:
    #                 return f"Error creating folder: {str(e)}"
            
            
    #         else:
    #             continue

  
    # ds.close()
    # end = datetime.now()
    # print('Time taken:', end - start)

    # return "create_weather data ended"

def create_weather_data_json_per_point_all_years(start, end):
    list_of_ds = []
    for year in range(start, end + 1):
        ds = create_composed_netcdf(year)
        list_of_ds.append(ds)

    ### open the list of composed datasets

    
    variable_names = ['tas', 'tasmin', 'tasmax', 'sfcWind', 'rsds', 'pr', 'hurs']
    

# data points to db --- probably obsolete ---
def create_all_point_data_files(year): 
    # Load NetCDF file using xarray
    ds = create_composed_netcdf(year)

    # Extract coordinates and data variables
    times = ds['time'].values
    lats = ds['lat'].values
    lons = ds['lon'].values

    # Iterate over time, latitude, and longitude
    for t_idx, time in enumerate(times):
        for lat_idx, lat in enumerate(lats):
            for lon_idx, lon in enumerate(lons):
                # Extract data variables for the current time, lat, lon
                date = pd.Timestamp(time).date()
                tas = ds['tas'][t_idx, lat_idx, lon_idx].values
                tasmin = ds['tasmin'][t_idx, lat_idx, lon_idx].values
                tasmax = ds['tasmax'][t_idx, lat_idx, lon_idx].values
                sfcwind = ds['sfcWind'][t_idx, lat_idx, lon_idx].values
                rsds = ds['rsds'][t_idx, lat_idx, lon_idx].values
                pr = ds['pr'][t_idx, lat_idx, lon_idx].values
                hurs = ds['hurs'][t_idx, lat_idx, lon_idx].values

                # Create a Point object with lat and lon
                point = Point(lon, lat)

                # Create a WeatherData instance
                weather_data = WeatherData(
                    point=point,
                    lat=lat,
                    lon=lon,
                    date=date,
                    tas=tas,
                    tasmin=tasmin,
                    tasmax=tasmax,
                    sfcwind=sfcwind,
                    rsds=rsds,
                    pr=pr,
                    hurs=hurs
                )

                # Save WeatherData instance to the database
                weather_data.save()

    # Close the NetCDF dataset
    ds.close()
    

def get_available_climate_data(start_date, end_date, lat, lon):
    print('get_available_climate_data')
    year = '2007'
    start = datetime.now()
    # Open the NetCDF file
    paths_dict = create_path_list_dict()
    paths_list = paths_dict[year]
    start_date_np = np.datetime64(start_date)
    end_date_np = np.datetime64(end_date)
    


    data_dict = {
        'tas': [], 
        'tasmin': [],
        'tasmax': [],
        'sfcWind': [],
        'rsds': [],
        'pr': [],
        'hurs': []
    }

    for dataset in  paths_list:
        print("open dataset ", dataset)
        ds = xr.open_dataset(dataset)

        time_var = ds['time']
        lat_var = ds['lat']
        lon_var = ds['lon']

        
        var_name = list(ds.variables.keys())[-1]
        time_indices = (time_var >= start_date_np) & (time_var <= end_date_np)

        var_data = ds[var_name].isel(time=time_indices, lat=200, lon=200)
        data_dict[var_name] = list(var_data.values)
        np_array = var_data.values
        rounded_floats = [round(float(value), 1) for value in np_array]
        data_dict[var_name] = rounded_floats
        
        ds.close()

        #filenameing
        
    def to_three_digit_str(number):
        if number < 100 and number >= 10:
            return '0' + str(number)
        elif number < 10:
            return '00' + str(number)
        else:
            return str(number)
    
    with open ('/app/monica/climate_data/test.json', 'w') as f:
        json.dump(data_dict, f)

    end = datetime.now()
    print('Time taken:', end - start)

    return json.dumps(data_dict)


def process_point(lat_idx, lon_idx, lat_lon_mask, ds, year):
    if lat_lon_mask['mask'][lat_idx][lon_idx]:
        lat = lat_lon_mask['lat'][lat_idx]
        lon = lat_lon_mask['lon'][lon_idx]
        point_data = ds.sel(lat=lat, lon=lon, method='nearest')
        point_json = {
            '3': point_data['tasmin'].values.tolist(),
            '4': point_data['tas'].values.tolist(),
            '5': point_data['tasmax'].values.tolist(),
            '6': point_data['pr'].values.tolist(),
            '8': point_data['rsds'].values.tolist(),
            '9': point_data['sfcWind'].values.tolist(),
            '12': point_data['hurs'].values.tolist()
        }
        file_path = f'/app/monica/climate_data/{lat_idx}/{lon_idx}/{year}.json'
        with open(file_path, 'w') as f:
            json.dump(point_json, f)
        print(f"File created: {file_path}")

def create_weather_data_json_per_point_and_year(year):
    start = datetime.now()
    ds = create_composed_netcdf(year)
    variable_names = ['tas', 'tasmin', 'tasmax', 'sfcWind', 'rsds', 'pr', 'hurs']
    with open('/app/monica/climate_data/lat_lon_mask.json') as f:
        lat_lon_mask = json.load(f)

    # for TESTPURPOSES::
    lat_lon_mask['lat_idx'] = [200, 201, 202, 203, 204]
    lat_lon_mask['lon_idx'] = [200, 201, 202, 203, 204]

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for lat_idx in lat_lon_mask['lat_idx']:
            for lon_idx in lat_lon_mask['lon_idx']:
                print(f"Processing {lat_idx} {lon_idx}")
                futures.append(
                    executor.submit(process_point, lat_idx, lon_idx, lat_lon_mask, ds, year)
                )

        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Check if any exceptions occurred
            except Exception as e:
                print(f"Error: {e}")

    ds.close()
    end = datetime.now()
    print('Time taken:', end - start)

    return "create_weather_data ended"
