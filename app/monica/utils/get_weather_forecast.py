import requests
from xml.etree import ElementTree
from datetime import datetime
from pathlib import Path
import xarray as xr
import os
from datetime import datetime

# Constants
BASE_CATALOG_URL = "https://esgf-data.dwd.de/thredds/catalog/esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS21/svhYYYY{month:02}01/sfc{year}{month:02}01/{scenario}/DWD-EPISODES2022/v1-r1/day/{variable}/"
SCENARIOS = ['r1i1p1', 'r2i1p1', 'r3i1p1']
VARIABLES = ['hurs', 'pr', 'psl', 'rsds', 'sfcWind', 'tas', 'tasmax', 'tasmin']
THREDDS_NAMESPACE = {"thredds": "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"}

def get_download_url(year, month, scenario, variable):
    """Get the latest catalog URL for the specified year, month, and scenario."""

    # get the version folder's name
    catalog_url = f"{BASE_CATALOG_URL.format(year=year, month=month, scenario=scenario,variable=variable)}catalog.xml"
    catalog = requests.get(catalog_url)
    catalog_tree = ElementTree.fromstring(catalog.content)
    
    catalog = catalog_tree.findall(".//thredds:catalogRef", THREDDS_NAMESPACE)
    latest_versions = []
    for catalog_ref in catalog:
        latest_versions.append(catalog_ref.attrib['name'])
    latest_version = max(latest_versions)

    # compose catalog url for the latest version
    latest_version_url = f"{BASE_CATALOG_URL.format(year=year, month=month, scenario=scenario,variable=variable)}{latest_version}/catalog.xml"
    
    # Get the dataset name/ urlPath
    dataset_name_reponse = requests.get(latest_version_url)
    dataset_name_catalog_tree = ElementTree.fromstring(dataset_name_reponse.content)
    dataset_name_catalog = dataset_name_catalog_tree.findall(".//thredds:dataset", THREDDS_NAMESPACE)
    dataset_path = ''
    for dataset in dataset_name_catalog:
        if dataset.attrib.get('urlPath'):
            dataset_path = dataset.attrib['urlPath']

    https_download_url = f"https://esgf-data.dwd.de/thredds/fileServer/{dataset_path}"
    return https_download_url


def get_local_path():
    """Get the base local path for storing NetCDF forecast files."""
    local = Path(__file__).resolve().parent.parent
    return local / 'climate_netcdf_forecast'

def fetch_available_variables(catalog_url):
    """Fetch available variables from the catalog XML, considering namespaces."""
    response = requests.get(catalog_url)
    response.raise_for_status()

    tree = ElementTree.fromstring(response.content)
    # Find all catalogRef elements within the namespace
    variables = [
        ref.attrib.get("name") for ref in tree.findall(".//thredds:catalogRef", THREDDS_NAMESPACE)
    ]
    
    return variables
# variables = ['hurs', 'pr', 'psl', 'rsds', 'sfcWind', 'tas', 'tasmax', 'tasmin']





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

def automated_thredds_download():
    """Main function to automate downloads of variables across scenarios."""
    now = datetime.now()
    year = now.year
    month = now.month

    local_path = get_local_path()

    # Step 1: Iterate through scenarios
    try:
        for scenario in SCENARIOS:
            for variable in VARIABLES:
                try:
                    print(f"Processing variable '{variable}' for scenario '{scenario}'...")
                    nc_file_url = get_download_url(year, month, scenario, variable)
                    print(f"Download URL: {nc_file_url}")
                    save_path = f"{local_path}/{scenario}/"
                    download_and_save_nc_file(nc_file_url, save_path)
                except ValueError as e:
                    print(f"Skipping {variable} for scenario {scenario}: {e}")
    except ValueError as e:
        print(f"Download of forecast data failed: {e}")

    else:
        print("Download of forecast data completed successfully.")
        try:
            for scenario in SCENARIOS:
                folder_path = f"{local_path}/{scenario}/"
                netcdf_paths = [f'{folder_path}/{nc}' for nc in os.listdir(folder_path) if nc.endswith('.nc')]
                ds = xr.open_mfdataset(netcdf_paths, combine='by_coords', compat='override')
                dates = netcdf_paths[0].split('_')[-1].split('.')[0]
                filename = f'forecast_{scenario}_{dates}.nc'
                file_path = f"{local_path}/{filename}"
                ds.to_netcdf(file_path)
                ds.close()
        except Exception as e:
            print(f"Combining NetCDF files failed: {e}")

    # TODO:  Implement the deletion of obsolete files

    

    
        
