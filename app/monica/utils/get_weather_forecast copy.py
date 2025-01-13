# https://esgf-data.dwd.de/thredds/catalog/esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS21/svhYYYY0101/catalog.html

# https://esgf-data.dwd.de/thredds/catalog/esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS21/svhYYYY0101/sfc20250101/r1i1p1/DWD-EPISODES2022/v1-r1/day/hurs/catalog.html

# from datetime import datetime

# def build_url():

#     url = 'https://esgf-data.dwd.de/thredds/catalog/esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS21/'
#     now = datetime.now()
#     month = now.month
#     year = now.year
#     url += f'svhYYYY{month:02}01/sfc{year}0101/r1i1p1/DWD-EPISODES2022/v1-r1/day/catalog.html'

#     return url
import requests
from xml.etree import ElementTree
from datetime import datetime
from pathlib import Path

SCENARIOS = ['r1i1p1, r2i1p1']
BASE_CATALOG_URL = "https://esgf-data.dwd.de/thredds/catalog/esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS21/"
DAY_FOLDER_TEMPLATE = "svhYYYY{month:02}01/sfc{year}{month:02}01/r1i1p1/DWD-EPISODES2022/v1-r1/day/catalog.xml"

# svhYYYY0101/sfc20250101/r1i1p1/DWD-EPISODES2022/v1-r1/day/hurs/v20250104/catalog.html?dataset=esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS21/svhYYYY0101/sfc20250101/r1i1p1/DWD-EPISODES2022/v1-r1/day/hurs/v20250104/hurs_day_GCFS21--DWD-EPISODES2022--DE-0075x005_sfc20250101_r1i1p1_20250101-20250630.nc
def build_catalog_url(year, month):
    return f"{BASE_CATALOG_URL}{DAY_FOLDER_TEMPLATE.format(year=year, month=month)}"

def get_latest_version_folder(catalog_url, variable):
    response = requests.get(catalog_url)
    response.raise_for_status()
    
    tree = ElementTree.fromstring(response.content)
    version_folder = None

    # Parse XML to find the folder for the desired variable
    for element in tree.iter("dataset"):
        name = element.attrib.get("name", "")
        if name.startswith(variable):
            version_folder = name.split("/")[0]
            break

    if not version_folder:
        raise ValueError("No version folder found in catalog.")

    return version_folder

def get_nc_file_url(base_url, version_folder, variable):
    variable_catalog_url = f"{base_url}{variable}/{version_folder}/catalog.xml"
    response = requests.get(variable_catalog_url)
    response.raise_for_status()

    tree = ElementTree.fromstring(response.content)
    nc_file_url = None

    # Find the .nc file URL
    for element in tree.iter("dataset"):
        name = element.attrib.get("name", "")
        if name.endswith(".nc"):
            nc_file_url = element.attrib.get("urlPath")
            break

    if not nc_file_url:
        raise ValueError("No .nc file found in catalog.")

    return f"https://esgf-data.dwd.de/thredds/fileServer/{nc_file_url}"

def automated_thredds_download(variable="hurs"):
    now = datetime.now()
    year = now.year
    month = now.month

    # Step 1: Build catalog URL
    catalog_url = build_catalog_url(year, month)

    # Step 2: Get the latest version folder for the variable
    version_folder = get_latest_version_folder(catalog_url, variable)

    # Step 3: Get the .nc file URL
    nc_file_url = get_nc_file_url(BASE_CATALOG_URL, version_folder, variable)

    print("Download URL:", nc_file_url)

    # Step 4: Download the file
    response = requests.get(nc_file_url)
    response.raise_for_status()

    filename = nc_file_url.split("/")[-1]
    with open(filename, "wb") as file:
        file.write(response.content)
    
    print(f"Downloaded: {filename}")

# Example Usage
# automated_thredds_download()

def get_path():
    local = Path(__file__).resolve().parent.parent
    local = Path.joinpath(local, 'climate_netcdf_forcast')
    return local
