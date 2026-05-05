"""
This module automates the download of weather forecast data from the DWD Climate Data Center.
It is used in the Django management command 'import_forecast_data.py' to download and convert the forecast data to combined NetCDF files.
"""
import requests
from xml.etree import ElementTree
from datetime import datetime, date
from pathlib import Path
import xarray as xr
import numpy as np
import os
from django.core.cache import cache
from django.conf import settings
from dateutil.relativedelta import relativedelta
from monica.utils import monica_constants



# TODO: Transport errormessage to management command: if no newer files are available and if download failed

def get_download_url(scenario, variable):
    """Get the latest catalog URL for the specified year, month, and scenario."""

    today = datetime.today()
    year = today.year
    month = today.month
    future_date = today + relativedelta(months=+6)

    # Move to the first day of the *next* month, then subtract one day
    last_day_of_month = (future_date.replace(day=1) + relativedelta(months=+1)) - relativedelta(days=1)

    # get the version folder's name
    try:
        catalog_url = f"{monica_constants.BASE_CATALOG_URL.format(year=year, month=month, scenario=scenario,variable=variable)}catalog.xml"
        
        catalog = requests.get(catalog_url)
        catalog_tree = ElementTree.fromstring(catalog.content)
        
        catalog = catalog_tree.findall(".//thredds:catalogRef", monica_constants.THREDDS_NAMESPACE)
        latest_versions = []
        for catalog_ref in catalog:
            latest_versions.append(catalog_ref.attrib['name'])
        latest_version = max(latest_versions)

        # compose catalog url for the latest version
        latest_version_url = f"{monica_constants.BASE_CATALOG_URL.format(year=year, month=month, scenario=scenario,variable=variable)}{latest_version}/catalog.xml"
        
        # Get the dataset name/ urlPath
        dataset_name_reponse = requests.get(latest_version_url)
        dataset_name_catalog_tree = ElementTree.fromstring(dataset_name_reponse.content)
        dataset_name_catalog = dataset_name_catalog_tree.findall(".//thredds:dataset", monica_constants.THREDDS_NAMESPACE)
        dataset_path = ''
        for dataset in dataset_name_catalog:
            if dataset.attrib.get('urlPath'):
                dataset_path = dataset.attrib['urlPath']

        print('https_download_url: ', monica_constants.DWD_THREDDS_DOWNLOAD_URL.format(dataset_path=dataset_path))
        return {'success': True, 'url':monica_constants.DWD_THREDDS_DOWNLOAD_URL.format(dataset_path=dataset_path)}
    
    except Exception as e:
        print(f"Error fetching download URL: {e}")
        return {'success': False, 'error': str(e)}
    
    


def fetch_available_variables(catalog_url):
    """Fetch available variables from the catalog XML, considering namespaces."""
    response = requests.get(catalog_url)
    response.raise_for_status()

    tree = ElementTree.fromstring(response.content)
    # Find all catalogRef elements within the namespace
    variables = [
        ref.attrib.get("name") for ref in tree.findall(".//thredds:catalogRef", monica_constants.THREDDS_NAMESPACE)
    ]
    # variables = ['hurs', 'pr', 'psl', 'rsds', 'sfcWind', 'tas', 'tasmax', 'tasmin']
    return variables


def get_last_valid_forecast_date():
    nc_folder_path = settings.MONICA_NETCDF_FORECAST_DIR
    nc_folder_path = os.path.join(nc_folder_path, 'r1i1p1/')
    netcdf_paths = [f'{nc_folder_path}/{nc}' for nc in os.listdir(nc_folder_path) if nc.endswith('.nc')]
    nc_path = netcdf_paths[0]
    ds = xr.open_dataset(nc_path)
    times = ds.time[:].values
    last_valid_date = times[-1]
    print('last_valid_date: ', last_valid_date)
    return last_valid_date.astype('datetime64[D]').astype(date)



def delete_old_files(folder_path, new_files):
    """Delete old NetCDF files from the folder that are not in new_files list."""
    try:
        print('delete_old_files: ', folder_path, new_files)
        for file in os.listdir(folder_path):
            print('delete_old_files: ', file)
            if file.endswith('.nc') and file not in new_files:
                file_path = os.path.join(folder_path, file)
                print(f"Deleting old file: {file_path}")
                os.remove(file_path)
    except Exception as e:
        print(f"Error deleting old files: {e}")


def download_and_save_nc_file(nc_url, save_path):
    """Download and save the NetCDF file to the specified local path."""
    response = requests.get(nc_url)
    response.raise_for_status()

    filename = nc_url.split("/")[-1]
    save_path = Path(save_path)
    save_path = save_path / filename
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, "wb") as file:
        file.write(response.content)

    print(f"Downloaded: {filename} to {save_path}")
    return filename

def correct_dataset_units(ds):
    """Correct the units of the dataset variables if necessary."""
    for var in ds.data_vars:
        if var in ('tas', 'tasmin', 'tasmax'):
            ds[var] = ds[var] - 273.15
            ds[var].attrs['units'] = '°C'
        if var == 'pr':
            ds[var] = ds[var] * 60 * 60 * 24
            ds[var].attrs['units'] = 'mm/day'
        if var == 'rsds':
            ds[var] = ds[var] * 10
            ds[var].attrs['units'] = 'W/m²'
    return ds


def automated_thredds_download():
    """
    Main function to automate downloads of variables across climate-scenarios.
    """


    # Step 1: Iterate through scenarios and variables
    
    for scenario in monica_constants.SCENARIOS:
        new_files = [] 
        folder_path = f"{settings.MONICA_NETCDF_FORECAST_DIR}/{scenario}/"
        for variable in monica_constants.VARIABLES:
            print(f"Processing variable '{variable}' for scenario '{scenario}'...")

            nc_file_url_message = get_download_url(scenario, variable)
            if nc_file_url_message['success']:

                downloaded_file = download_and_save_nc_file(nc_file_url_message['url'], folder_path)
                new_files.append(downloaded_file)
                print('new_files: ', new_files)
            else:
                print(f"Failed to download {variable} for scenario {scenario}: {nc_file_url_message['error']}")


        if  new_files != []:
            print('new_files: ', new_files)
            print(f"Deleting old files for scenario '{scenario}'...")
            delete_old_files(folder_path, new_files)


    old_combined_ncs = [f'{settings.MONICA_NETCDF_FORECAST_DIR}/{nc}' for nc in os.listdir(settings.MONICA_NETCDF_FORECAST_DIR) if nc.endswith('.nc')]
    # print('old_ncs: ', old_ncs)
    new_combined_ncs = []

    # Combine NetCDF files  into a single file for each scenario
    try:
        for scenario in monica_constants.SCENARIOS:
            folder_path = f"{settings.MONICA_NETCDF_FORECAST_DIR}/{scenario}/"
            netcdf_paths = [f'{folder_path}/{nc}' for nc in os.listdir(folder_path) if nc.endswith('.nc')]
            
            dates = netcdf_paths[0].split('_')[-1].split('.')[0]
            filename = f'forecast_{scenario}_{dates}.nc'
            file_path = f"{settings.MONICA_NETCDF_FORECAST_DIR}/{filename}"
            if file_path not in old_combined_ncs:
                ds = xr.open_mfdataset(netcdf_paths, combine='by_coords', compat='override')
                ds = correct_dataset_units(ds)
                ds.to_netcdf(file_path)
                ds.close()
                new_combined_ncs.append(file_path)
                
        print('old_ncs: ', old_combined_ncs)
        print('new_ncs: ', new_combined_ncs)
        if old_combined_ncs != [] and new_combined_ncs != [] and old_combined_ncs.sort() != new_combined_ncs.sort():
            for old_nc in old_combined_ncs:
                os.remove(old_nc)

        
    except Exception as e:
        print(f"Combining NetCDF files failed: {e}")




    # TODO:  Implement the deletion of obsolete files!!!

    

    
        
