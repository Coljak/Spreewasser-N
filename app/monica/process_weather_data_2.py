"""
NETCDFs are processed in this code to create JSON files for each point in the bounding box.
In this code, the paths are set to those of the local repository and not those of the docker container.
This is to maximise CPU availability.
"""


import xarray as xr
import numpy as np
from datetime import datetime
import os
import pandas as pd
import json
import concurrent.futures

# from monica.climate_data.lat_lon_mask  import lat_lon_mask 
# lat  52.759267368766714  Index:  255
# lat  51.869135772975724  Index:  354
# lon  13.49151000957146  Index:  543
# lon  14.52972381380014  Index:  617


SWN_BOUNDING_JSON = {
  "type": "Polygon",
  "coordinates": [
    [
      [
        13.481181,
        51.875618
      ],
      [
        13.481181,
        52.76205
      ],
      [
        14.526383,
        52.76205
      ],
      [
        14.526383,
        51.875618
      ],
      [
        13.481181,
        51.875618
      ]
    ]
  ]
}

def create_path_list_dict():
    """
    This function creates a dictionary of all weather data. 
    dir_paths_dict = {
        '2011': ['/app/thredds_data/DWD_Data/zalf_hurs_amber_2021_v1-0_cf_v6.nc.nc', ...],
    """

    print('Path:', os.getcwd())
    # dir_list = os.listdir('/app/thredds_data/DWD_Data/')
    dir_list = os.listdir('./thredds_data/data/DWD_Data/')
    dir_list.sort()
    dir_paths_dict = {}
    for dir in dir_list:
        year = dir.split('_')[3]
        dir_paths_dict[year] = []
    for dir in dir_list:
        year = dir.split('_')[3]
        dir_paths_dict[year].append('./thredds_data/data/DWD_Data/' + dir)
        
    return dir_paths_dict

def create_composed_netcdf(year):
    try:
        year = str(year)
    except:
        pass

    return xr.open_mfdataset(create_path_list_dict()[year], combine='by_coords')



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
        file_path = f'./app/monica/climate_data/{lat_idx}/{lon_idx}/{year}.json'
        with open(file_path, 'w') as f:
            json.dump(point_json, f)
        print(f"File created: {file_path}")

def create_weather_data_json_per_point_and_year(year):
    start = datetime.now()
    ds = create_composed_netcdf(year)
    with open('./app/monica/climate_data/lat_lon_mask.json') as f:
        lat_lon_mask = json.load(f)

    # # for TESTPURPOSES::
    # lat_lon_mask['lat_idx'] = [200, 201, 202, 203, 204]
    # lat_lon_mask['lon_idx'] = [200, 201, 202, 203, 204]
    lat_idx_list = lat_lon_mask['lat_idx'][255:355] # for production [:]
    lon_idx_list = lat_lon_mask['lon_idx'][543:618]

    # GET DATA for SWN BOUNDING BOX
    lat_lon_mask['lat']

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for lat_idx in lat_idx_list:
            for lon_idx in lon_idx_list:
                    # This is the startingpoint for 2007
                # if (lat_idx > 360) or (lat_idx == 360 and lon_idx > 509 and lon_idx < 530) or (lat_idx == 360 and lon_idx > 349 and lon_idx < 370
                # ) or (lat_idx == 360 and lon_idx > 600):
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

    return f"create_weather_data ended for year {year}"
