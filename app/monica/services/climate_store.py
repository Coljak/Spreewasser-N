import xarray as xr
from datetime import datetime
from monica.utils import monica_constants
from pathlib import Path
import glob



FORECAST = None
HINDCAST = None

def load_hindcast():
    climate_data_path = Path(__file__).resolve().parent.parent.joinpath('climate_netcdf')

    this_year = datetime.now().year
    start_year = this_year - 3

    path_list = []
    for _, value in monica_constants.CLIMATE_VARIABLES.items():

        for year in range(start_year, this_year + 1):
            file_path = f"{climate_data_path}/zalf_{value.lower()}_amber_{year}_v1-0.nc"
            path_list.append(file_path)


    hindcast = xr.open_mfdataset(
            path_list,
            combine='by_coords',
            chunks={'time': 61},
            parallel=False
        )
    return hindcast


def load_forecast():
    """
    Initializes a lazily-loaded xarray dataset for reuse across requests.
    This function loads the NetCDF files for each forecast scenario.
    This is done to avoid opening and closing the files for each request.
    """
    climate_data_path = Path(__file__).resolve().parent.parent.joinpath('climate_netcdf_forecast')
    print(' climate_data_path: ', type(climate_data_path), climate_data_path)
    # TODO - deal with multiple scenarios!!
    for scenario in [monica_constants.SCENARIOS[0]]:
        print(f"Loading forecast for scenario '{scenario}'...")
        files = glob.glob(f"{str(climate_data_path)}/forecast_{scenario}_*.nc")
        print(f"Found forecast files: {files}")

        file_path = files[0] # get the latest scenario if multiple exist
        
        forecast = xr.open_dataset(
                file_path,
                chunks={'time': 61},
            )

    return forecast

def get_forecast():
    global FORECAST
    if FORECAST is None:
        FORECAST = load_forecast()
    return FORECAST

def get_hindcast():
    global HINDCAST
    if HINDCAST is None:
        HINDCAST = load_hindcast()
    return HINDCAST

def reload_all():
    global FORECAST, HINDCAST
    FORECAST = None
    HINDCAST = None