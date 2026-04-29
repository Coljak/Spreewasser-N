"""
These are specific constants for MONICA that are used across the application.
"""
# all relevant climate variables. 
# The keys are the ones used in the  MONICA model code, the values are the corresponding variable names in the NetCDF files.
CLIMATE_VARIABLES = { 
    '3': 'tasmin',
    '4': 'tas',
    '5': 'tasmax',
    '6': 'pr',
    '8': 'rsds',
    '9': 'sfcWind',
    '12': 'hurs'
    }
VARIABLES = ['hurs', 'pr', 'rsds', 'sfcWind', 'tas', 'tasmax', 'tasmin']
VARIABLES_LOWER = [var.lower() for var in VARIABLES] # 'psl'could also be downloaded



# START_YEAR handles the year of first dataset and in the load dataset function
START_YEAR = 2007 
# Set the forecast scenarios that are supposed to be available for model calculations.
SCENARIOS = ['r1i1p1', 'r2i1p1', 'r3i1p1']

# paths to weather data
BASE_CATALOG_URL = "https://esgf-data.dwd.de/thredds/catalog/esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS22/svh2023{month:02}01/sfc{year}{month:02}01/{scenario}/DWD-EPISODES2022/v1-r1/day/{variable}/"

BASE_DOWNLOAD = "https://esgf-data.dwd.de/thredds/fileServer/esgf3/data/climatepredictionsde/seasonal/output/public/DE-0075x005/DWD/GCFS22/"

THREDDS_NAMESPACE = {"thredds": "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"}
DWD_THREDDS_DOWNLOAD_URL = "https://esgf-data.dwd.de/thredds/fileServer/{dataset_path}"

# layerAggOp
OP_AVG = 0
OP_MEDIAN = 1
OP_SUM = 2
OP_MIN = 3
OP_MAX = 4
OP_FIRST = 5
OP_LAST = 6
OP_NONE = 7
OP_UNDEFINED_OP_ = 8


ORGAN_ROOT = 0
ORGAN_LEAF = 1
ORGAN_SHOOT = 2
ORGAN_FRUIT = 3
ORGAN_STRUCT = 4
ORGAN_SUGAR = 5
ORGAN_UNDEFINED_ORGAN_ = 6