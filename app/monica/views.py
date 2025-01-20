
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Transform
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from django.db.models import Q

from .run_consumer_swn import run_consumer
from . import models as m_models
from . import monica_io3_swn
from swn import models as swn_models
from .forms import *
from buek.views import get_soil_profile
from buek import models as buek_models
from .climate_data.lat_lon_mask import lat_lon_mask
from .monica_events import *
from .utils import save_monica_project

from pathlib import Path
from netCDF4 import Dataset, MFDataset
import xarray as xr
import dask.array as da
import os
import numpy as np
from dateutil import parser
from cftime import num2date, date2num, date2index
import time
import json
import zmq
import csv
import copy
# create a new monica env
# from ...xx_obsolete import climate
from .process_weather_data import *
from datetime import datetime, timedelta
from dask.diagnostics import ProgressBar
import dask
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="xarray")


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
#-------------------------- Monica Interface --------------------------#


# all relevant climate variables. The key is already the the correct key for  MONICA climate jsons
CLIMATE_VARIABLES = { 
    '3': 'tasmin',
    '4': 'tas',
    '5': 'tasmax',
    '6': 'pr',
    '8': 'rsds',
    '9': 'sfcWind',
    '12': 'hurs'
    }


# not in use
def get_lat_lon_as_index(lat, lon):
    """
    Returns the index of the closest lat, lon to the given lat, lon in the netCDF grid. Used for matching differntly scaled grids.
    """
    lats = lat_lon_mask['lat']
    
    lons = lat_lon_mask['lon']
    lat_idx = 0
    lon_idx = 0
    for i, lat_ in enumerate(lats):
        if lat_ < lat:
            lat_idx = i
            break
    
    for j, lon_ in enumerate(lons):
        if lon_ > lon:
            lon_idx = j
            break
   
    if (lats[lat_idx] + lats[lat_idx-1]) / 2 < lat:
        print("lat is in if")
        lat_idx = lat_idx - 1

    if (lons[lon_idx] + lons[lon_idx-1]) / 2 > lon:
        print("lon is in if")
        lon_idx = lon_idx - 1

    print('lat', lats[lat_idx], 'lon_idx', lons[lon_idx])
    return (lat_idx, lon_idx)


def load_netcdf_to_memory():
    """
    Loads all netcdf files of at least the past two years into memory. 
    This is done to avoid opening and closing the files for each request.
    """
    climate_data_path = Path(__file__).resolve().parent.joinpath('climate_netcdf')

    this_year = datetime.now().year
    start_year = this_year - 3

    path_list = []
    for _, value in CLIMATE_VARIABLES.items():

        for year in range(start_year, this_year + 1):
            file_path = f"{climate_data_path}/zalf_{value.lower()}_amber_{year}_v1-0.nc"
            path_list.append(file_path)


    climate = xr.open_mfdataset(path_list, combine='by_coords', chunks={'time':150, 'lat': 100, 'lon': 100}) 
    climate_first_date = climate['time'][0]
    climate_last_date = climate['time'][-1]
    return climate, climate_first_date, climate_last_date

# TODO REACTIVATE - only deactivated to prevet long loading times
# CLIMATE_DATES = load_netcdf_to_memory()
# CLIMATE = CLIMATE_DATES[0]
# CLIMATE_FIRST_DATE = CLIMATE_DATES[1]
# CLIMATE_LAST_DATE = CLIMATE_DATES[2]

# def get_climate_data_as_json_new(start_date, end_date, lat_idx, lon_idx):
#     start = datetime.now()
#     climate_json = {}
#     # with ProgressBar():
#     climate_slice = CLIMATE.sel(time=slice(start_date, end_date)).isel(lat=lat_idx, lon=lon_idx)
#     # Shows a progress bar for Dask computations


#     for key, value in CLIMATE_VARIABLES.items():
#         climate_json[key] = climate_slice[value].values.tolist()
#     print('Time elapsed in get_climate_data_as_json_new: ', datetime.now() - start)
#     return climate_json


# used
def get_climate_data_as_json(start_date, end_date, lat_idx, lon_idx):
    """Returns the climate data as json using monica's keys for the given start and end date and the given lat and lon index"""
    print("get_climate_data_as_json", start_date, end_date, lat_idx, lon_idx)

    # opening with MFDataset does not work, because time is not an unlimited dimension in the NetCDF files
    start = datetime.now()
    climate_json = { 
        '3': [],
        '4': [],
        '5': [],
        '6': [],
        '8': [],
        '9': [],
        '12': [],
        }
    climate_data_path = Path(__file__).resolve().parent.joinpath('climate_netcdf')

    for year in range(start_date.year, end_date.year + 1):
        print('climate data for loop', year)
        for key, value in CLIMATE_VARIABLES.items():
            
            file_path = f"{climate_data_path}/zalf_{value.lower()}_amber_{year}_v1-0.nc"
            print("filepath: ", file_path,  "getting key:", key)
            nc = Dataset(file_path, 'r')
            # print('climate data check 1')
            start_idx = 0
            end_idx = len(nc['time']) + 1
            if year == start_date.year:
                start_idx = date2index(start_date, nc['time'])
            if year == end_date.year:
                end_idx = date2index(end_date, nc['time']) +1

            values = nc.variables[value][start_idx:end_idx, lat_idx, lon_idx]
            values = values.tolist()

            climate_json[key].extend(values)

            nc.close()

            print(year, value, key)
    print('Time elapsed in get_climate_data_as_json: ', datetime.now() - start)
    climate_json['8'] = [x / 100 for x in climate_json['8']]
    return climate_json

### MONICA VIEWS ###



def create_monica_env_from_json(json_data):
    error = []
   
    cropRotation = []
    
    for r in json_data['rotation']:
        rotation = {}

        
        worksteps = []
        for k, v in r.items():
            # print("K: ", k)
            if k == 'sowingWorkstep':
                for ws in v:
                    if ws.get('options').get('species') is None:
                        error.append('Species not selected')
                    if ws.get('date') is None:
                        error.append('Sowing date not selected')
                    else:
                        workstep = {"date":  ws.get('date'),               # "0000-10-13",
                                "type": "Sowing",
                                "crop": {
                                    # "is-winter-crop": True, # TODO is winter-crop is probably not required!!!
                                    "cropParams": {
                                        "species": {
                                        "=": m_models.SpeciesParameters.objects.get(id=ws.get('options').get('species')).to_json()
                                        },
                                        "cultivar": {
                                        "=": m_models.CultivarParameters.objects.get(id=ws.get('options').get('cultivar')).to_json()
                                        }
                                    },
                                    "residueParams": m_models.CropResidueParameters.objects.get(id=ws.get('options').get('cropResidue')).to_json()
                                }
                            }
                    
                        worksteps.append(workstep)
            elif k == 'harvestWorkstep':
                for ws in v:
                    workstep = {
                            "type": "Harvest",
                            "date": ws.get('date', None)               # "0001-05-21"
                        }
                    if workstep['date'] is not None:
                        worksteps.append(workstep)
            elif k == 'mineralFertilisationWorkstep':
                for ws in v:
                    workstep = {
                            "type": "mineralFertilisation",
                            "date": ws.get('date', None),
                            'amount'  : ws.get('amount', 0)            # "0001-05-21"
                        }
                    if workstep['date'] is not None:
                        worksteps.append(workstep)                   
            elif k == 'organicFertilisationWorkstep':
                for ws in v:
                    workstep = {
                            "type": "organicFertilisation",
                            "date": ws.get('date', None),
                            'amount'  : ws.get('amount', 0)          # "0001-05-21"
                        }
                    if workstep['date'] is not None:
                        worksteps.append(workstep)
            elif k == 'tillageWorkstep':
                for ws in v:
                    workstep = {
                            "type": "tillage",
                            "date": ws.get('date', None),
                            # 'depth'  : ws.depth            # "0001-05-21"
                        }
                    if workstep['date'] is not None:
                        worksteps.append(workstep)
            elif k == 'irrigationWorkstep':
                for ws in v:
                    workstep = {
                            "type": "Irrigation",
                            "date": ws.get('date', None),
                            'amount'  : [float(ws.get('options').get('amount', 0)), 'mm']  # "0001-05-21"
                        }
                    if workstep['date'] is not None:
                        worksteps.append(workstep)
            else:
                print("Workstep not found: ", k)

        worksteps = sorted(worksteps, key=lambda x: x['date'])
        rotation["worksteps"] = worksteps

        cropRotation.append(rotation)

    # print('cropRotation: ', cropRotation)
    cropRotations = None

      # end of replacement -------------------------------------------
    
    debugMode = True

    # soil profile
    # TODO implement landusage!!
    landusage = json_data.get('landusage', 'general')

    soil_profile_parameters = []
    
    # the corrected soil profile is retrieved either from location or the MonicaProject
    if json_data.get('soilProfileId', None) is None:
        lat = json_data.get('latitude')
        lon = json_data.get('longitude')
        soil_profile_parameters = get_soil_profile(landusage, lat, lon)['SoilProfileParameters']
    else:
        # TODO specify SoilProfile content Type!
        soil_profile_id = json_data.get('soilProfileId')
        soil_profile_parameters = buek_models.SoilProfile.objects.get(id=soil_profile_id).get_horizons_json()



    # TODO site parameters
    slope = 0
    height_nn = 0
    n_deposition = 30

   

    siteParameters = {
        "Latitude": float(json_data['latitude']),
        "Slope": slope,
        "HeightNN": [height_nn, "m"],
        "NDeposition": [n_deposition,"kg N ha-1 y-1"],
        "SoilProfileParameters": soil_profile_parameters
    }
    simulation_settings = json_data.get('userSimulationSettingsId')
    if simulation_settings is not None:
        simj = UserSimulationSettings.objects.get(id=simulation_settings).to_json()
    else:
        simj = UserSimulationSettings.objects.get(is_default=True).to_json() 
        
    user_crop_parameters_id = json_data.get('userCropParametersId')
    if user_crop_parameters_id is not None:
        user_crop_parameters = m_models.UserCropParameters.objects.get(id=user_crop_parameters_id).to_json()
    else:
        user_crop_parameters = m_models.UserCropParameters.objects.get(is_default=True).to_json()

    user_environment_parameters_id = json_data.get('userEnvironmentParametersId')
    if user_environment_parameters_id is not None:
        user_environment_parameters = m_models.UserEnvironmentParameters.objects.get(id=user_environment_parameters_id).to_json()
    else:
        user_environment_parameters = m_models.UserEnvironmentParameters.objects.get(is_default=True).to_json()


    user_soil_moisture_parameters_id = json_data.get('userSoilMoistureParametersId')
    if user_soil_moisture_parameters_id is not None:   
        user_soil_moisture_parameters = m_models.UserSoilMoistureParameters.objects.get(id=user_soil_moisture_parameters_id).to_json()
    else:
        user_soil_moisture_parameters = m_models.UserSoilMoistureParameters.objects.get(is_default=True).to_json()

    user_soil_temperature_parameters_id = json_data.get('userSoilTemperatureParametersId')
    if user_soil_temperature_parameters_id is not None:
        user_soil_temperature_parameters = m_models.SoilTemperatureModuleParameters.objects.get(id=user_soil_temperature_parameters_id).to_json()
    else:
        user_soil_temperature_parameters = m_models.SoilTemperatureModuleParameters.objects.get(is_default=True).to_json()

    user_soil_transport_parameters_id = json_data.get('userSoilTransportParametersId')
    if user_soil_transport_parameters_id is not None:
        user_soil_transport_parameters = m_models.UserSoilTransportParameters.objects.get(id=user_soil_transport_parameters_id).to_json()
    else:
        user_soil_transport_parameters = m_models.UserSoilTransportParameters.objects.get(is_default=True).to_json()

    user_soil_organic_parameters_id = json_data.get('userSoilOrganicParametersId')
    if user_soil_organic_parameters_id is not None:
        user_soil_organic_parameters = m_models.UserSoilOrganicParameters.objects.get(id=user_soil_organic_parameters_id).to_json()
    else:
        user_soil_organic_parameters = m_models.UserSoilOrganicParameters.objects.get(is_default=True).to_json()


    cpp = {
    "type": "CentralParameterProvider",
    "userCropParameters": user_crop_parameters,
    "userEnvironmentParameters": user_environment_parameters,
    "userSoilMoistureParameters": user_soil_moisture_parameters,
    "userSoilTemperatureParameters": user_soil_temperature_parameters,
    "userSoilTransportParameters": user_soil_transport_parameters,
    "userSoilOrganicParameters":user_soil_organic_parameters,
    "simulationParameters": simj, #UserSimulationSettings.objects.get(id=simulation_settings).to_json()
    "siteParameters": siteParameters
    }

     # get climate data from database
    # print("Lat lon: ", json_data['latitude'], json_data['longitude'])
    lat_idx, lon_idx = m_models.DWDGridAsPolygon.get_idx(float(json_data['latitude']), float(json_data['longitude']))
    
    # TODO use get_climate_data_as_json_new and activate CLIMATE_DATES
    climate_data = get_climate_data_as_json(parser.parse(json_data['startDate'].split('T')[0]), parser.parse(json_data['endDate'].split('T')[0]), lat_idx, lon_idx)
    #climate_data = get_climate_data_as_json_new(parser.parse(json_data['startDate'].split('T')[0]), parser.parse(json_data['endDate'].split('T')[0]), lat_idx, lon_idx)

    # print('available_climate_data', available_climate_data)
    # print("check 1")
    # print("Date type: ", type(json_data['startDate']), json_data['startDate'])
    start_date = json_data['startDate'].split('T')[0]
    end_date = json_data['endDate'].split('T')[0]
    # print("CLIMATE DATA START DATE ", start_date)
    # print("check 2")
    climate_json = {
        "type": "DataAccessor",
        "data": climate_data,
        "startDate": start_date,
        "endDate": end_date,
      }
    
      # events define the output.
    events = [
        "daily",
        [
            "Date",
            # "ETa/ETc",
            # "AbBiom",
            # [
            # "OrgBiom",
            # "Leaf"
            # ],
            # [
            # "OrgBiom",
            # "Fruit"
            # ],
            "Yield",
            "LAI",
            "Precip",
            [
            "Mois",
            [
                1,
                20
            ]
            ],
            [
            "Mois",
            [
                1,
                10,
                "AVG"
            ]
            ],
            [
            "SOC",
            [
                1,
                3
            ]
            ],
            "Tavg",
            "Globrad"
        ],
        "crop",
        [
            "CM-count",
            "Crop",
            [
            "Yield",
            "LAST"
            ],
            [
            "Date|sowing",
            "FIRST"
            ],
            [
            "Date|harvest",
            "LAST"
            ]
        ],
        "yearly",
        [
            "Year",
            [
            "N",
            [
                1,
                3,
                "AVG"
            ],
            "SUM"
            ],
            [
            "RunOff",
            "SUM"
            ],
            [
            "NLeach",
            "SUM"
            ],
            [
            "Recharge",
            "SUM"
            ]
        ],
        "run",
        [
            [
            "Precip",
            "SUM"
            ]
        ]
    ]

    # print("check 3")
    env = {
        "type": "Env",
        "debugMode": debugMode,
        "params": cpp,
        "cropRotation": cropRotation,
        "cropRotations": cropRotations,
        "events": swn_events,
        # "climateData": json.dumps(climate_json)
        "climateData": climate_json
    }



    return env
 
def msg_to_json(msg):
    """
    the json output of Monica is processed in this function so that every output 
    is a flat array with the length of the base array e.g. of dates for each output. 
    This is applied to all outputs such as 'daily', 'monthly, 'crop' etc.
    """
    # aggregation constants as dictionary from monica_io3.py
    aggregation_constants = {
        0: "AVG",
        1: "MEDIAN",
        2: "SUM",
        3: "MIN",
        4: "MAX",
        5: "FIRST",
        6: "LAST",
        7: "NONE",
        8: "UNDEFINED_OP"
    }
    # organ constants as dictionary from monica_io3.py
    organ_constants = {
        0: "ROOT",
        1: "LEAF",
        2: "SHOOT",
        3: "FRUIT",
        4: "STRUCT",
        5: "SUGAR",
        6: "UNDEFINED_ORGAN"
    }


    # print("msg_to_json")
    processed_msg = {}
    for_chart = {}
    for data_ in msg.get("data", []):
        results = data_.get("results", [])
        orig_spec = data_.get("origSpec", "")
        output_ids = data_.get("outputIds", [])
        # print('origSpec', orig_spec, 'output_ids', output_ids)

        orig_spec = orig_spec.replace("\"", "")
        
        for_chart[orig_spec] = {}
        for output_id, result_list in zip(output_ids, results):
            output_id["result"] = result_list
            try:
                output_id["jsonInput"] = json.loads(output_id["jsonInput"])
            except:
                pass
            # soil has layers, yield, LAI etc does not have layers
            if output_id["fromLayer"] == output_id["toLayer"] == -1:
                output_id["result_dict"] = {}
                name = output_id["name"]
                if output_id["organ"] != 6:
                    name = name + "_" + organ_constants[output_id["organ"]]
                    
                output_id["result_dict"][name] = result_list

                for_chart[orig_spec][name] = result_list
            elif output_id["layerAggOp"] != 7:
                output_id["result_dict"] = {}
                output_id["result_dict"][f"{output_id['name']}_{aggregation_constants[output_id['layerAggOp']]}"] = result_list

                for_chart[orig_spec][f"{output_id['name']}_{aggregation_constants[output_id['layerAggOp']]}"] = result_list
            elif (output_id["fromLayer"] != output_id["toLayer"]) and (output_id["layerAggOp"] == 7):
                # no aggregation of layers, but calculations for several layers
                output_id["result_dict"] = {}
                try:
                    for i in range(output_id["fromLayer"], output_id["toLayer"]+1):
                        # print("I: ", i)
                        output_id["result_dict"][f"{output_id['name']}_{i+1}"] = []
                        for j in range(len(result_list)): 
                            output_id["result_dict"][f"{output_id['name']}_{i+1}"].append(result_list[j][i])
                        for_chart[orig_spec][f"{output_id['name']}_{i+1}"] = output_id["result_dict"][f"{output_id['name']}_{i+1}"]
                except:
                    output_id["result_dict"]["error"] = "Error in processing results"
                    
        processed_msg[orig_spec] = {
            "output_ids": output_ids,     
        }
           
    return for_chart

def export_monica_result_to_csv(msg):
    """
    The csv export is the same as in the MONICA repository.
    """

    file_path = Path(__file__).resolve().parent
    
    file_name = 'monica_result_.csv'
    file_path = Path.joinpath(file_path, 'monica_csv_exports/', file_name)
    with open(file_path, 'w', newline='') as _:
        writer = csv.writer(_, delimiter=",")

        for data_ in msg.get("data", []):
            results = data_.get("results", [])
            orig_spec = data_.get("origSpec", "")
            output_ids = data_.get("outputIds", [])

            if len(results) > 0:
                writer.writerow([orig_spec.replace("\"", "")])
                for row in monica_io3_swn.write_output_header_rows(output_ids,
                                                                include_header_row=True,
                                                                include_units_row=True,
                                                                include_time_agg=False):
                    writer.writerow(row)

                for row in monica_io3_swn.write_output(output_ids, results):
                    writer.writerow(row)

            writer.writerow([])

def get_parameter_options(request, parameter_type, id=None):
    """
    Get choices for select boxes.
    """
    user = request.user.id
    print("GET PARAMETER OPTIONS: ", parameter_type, id,)
    if parameter_type == 'soil-moisture-parameters':
        options = UserSoilMoistureParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'soil-organic-parameters':
        options = UserSoilOrganicParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'soil-temperature-parameters':
        options = SoilTemperatureModuleParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'soil-transport-parameters':
        options = UserSoilTransportParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
        # options = UserSoilTransportParameters.objects.values('id', 'name')
    elif parameter_type == 'species-parameters':
        options = SpeciesParameters.objects.filter(Q(user=None) | Q(user=user)).values('id','name')
        # options = SpeciesParameters.objects.values('id', 'name')
    elif parameter_type == 'cultivar-parameters':
        if id is not None:
            # options = CultivarParameters.objects.filter(Q(user=None) | Q(user=user_id)).values('id','name')
            # TODO most of this is probably obsolete- no species --> no cultivar
            options = CultivarParameters.objects.filter(Q(species_parameters_id=id) & (Q(user=None) | Q(user=user))).values('id', 'name')
            if options.count() == 0:
                options = CultivarParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
        else:
            options = CultivarParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'crop-residue-parameters':
        if id is not None:
            options = CropResidueParameters.objects.filter(Q(species_parameters_id=id) & (Q(user=None) | Q(user=user))).values('id', 'name')
            if options.count() == 0:
                options = CropResidueParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
        else:
            options = CropResidueParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'organic-fertiliser-parameters':
        options = OrganicFertiliser.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'mineral-fertiliser-parameters':
        options = MineralFertiliser.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'user-crop-parameters':
        options = UserCropParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'user-environment-parameters':
        options = UserEnvironmentParameters.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'user-simulation-settings':
        options = UserSimulationSettings.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    elif parameter_type == 'monica-project':
        options = MonicaProject.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    else:
        options = []

    return JsonResponse({'options': list(options)})

def load_monica_project(request, id):

    context = {}
    project = MonicaProject.objects.get(pk=id)
    print("Monica Project: ", project)
    if not project:
        return JsonResponse({'message':{'success': False, 'message': 'Project not found'}})
    else:
        return JsonResponse({'message':{'success': True, 'message': f'Project {project.name} loaded'}, 'project': project.to_json()})


def delete_monica_project(request, id):
    print("DELETE MONICA PROJECT")
    if request.method == 'DELETE':
        try:
            project = MonicaProject.objects.get(pk=id)
            project.delete()
            return JsonResponse({'message': {'success': True, 'message': f'Project {project.name} deleted'}})
        except:
            return JsonResponse({'message': {'success': False, 'message': 'Project not found'}})
    
def save_monica_site(request):
    """
    Save a site to the database.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        lat = data.get('latitude', None)
        lon = data.get('longitude', None)
        name = data.get('name', None)
        altitude = data.get('altitude', 50) # TODO get altitude from dem
        slope = data.get('slope', 0)
        n_deposition = data.get('n_deposition', 11)
        # if data.get('buek_soil_profile', True) == True:

        soil_profile = data.get('soil_profile')

        if soil_profile is not None:
            return JsonResponse({'success': True, 'message': 'Site saved', 'site_id': site.id})
        else:
            return JsonResponse({'success': False, 'message': form.errors})
        

def create_monica_project(request):
    print("CREATE MONICA PROJECT\n", request.POST)

    project = save_monica_project.save_project(request, project_class=MonicaProject)

    return JsonResponse({'message': {'success': True, 'message': f'Project {project.name} saved'}, 'project_id': project.id, 'project_name': project.name})
        # else:
    # except:
    #     return JsonResponse({'message': {'success': False, 'message': form.errors}})


    
def modify_model_parameters(request, parameter, id, rotation=None):

    """
    Every Monica Parameter JSON can be modified and saved. 
    This function applies to all parameters, loads the from and saves the data.
    """
    # TODO Settings parameters are not yet implemented
    MODEL_FORM_MAPPING = {
        'species-parameters': {
            'model': SpeciesParameters,
            'form': SpeciesParametersForm,
            'modal_title': 'Modify Species Parameters',
            'modal_save_button': 'Save Species Parameters',
            'modal_save_as_button': 'Save as New Species Parameters',
        },
        'cultivar-parameters': {
            'model': CultivarParameters,
            'form': CultivarParametersForm,
            'modal_title': 'Modify Cultivar Parameters',
            'modal_save_button': 'Save Cultivar Parameters',
            'modal_save_as_button': 'Save as New Cultivar Parameters',
        },
        'crop-residue-parameters': {
            'model': CropResidueParameters,
            'form': CropResidueParametersForm,
            'modal_title': 'Modify Crop Residue Parameters',
            'modal_save_button': 'Save Crop Residue Parameters',
            'modal_save_as_button': 'Save as New Crop Residue Parameters',
        },
        'organic-fertiliser-parameters': {
            'model': OrganicFertiliser,
            'form': OrganicFertiliserForm,
            'modal_title': 'Modify Organic Fertiliser',
            'modal_save_button': 'Save Organic Fertiliser',
            'modal_save_as_button': 'Save as New Organic Fertiliser',
        },
        'mineral-fertiliser-parameters': {
            'model': MineralFertiliser,
            'form': MineralFertiliserForm,
            'modal_title': 'Modify Mineral Fertiliser',
            'modal_save_button': 'Save Mineral Fertiliser',
            'modal_save_as_button': 'Save as New Mineral Fertiliser',
        },
        'user-crop-parameters': {
            'model': UserCropParameters,
            'form': UserCropParametersForm,
            'modal_title': 'Modify Crop Parameters',
            'modal_save_button': 'Save Crop Parameters',
            'modal_save_as_button': 'Save as New Crop Parameters',
        },
        'user-environment-parameters': {
            'model': UserEnvironmentParameters,
            'form': UserEnvironmentParametersForm,
            'modal_title': 'Modify Environment Parameters',
            'modal_save_button': 'Save Environment Parameters',
            'modal_save_as_button': 'Save as New Environment Parameters',
        },
        'user-simulation-settings': {
            'model': UserSimulationSettings,
            'form': UserSimulationSettingsForm,
            'modal_title': 'Modify Simulation Settings',
            'modal_save_button': 'Save Simulation Settings',
            'modal_save_as_button': 'Save as New Simulation Settings',
        },
        'soil-moisture-parameters': {
            'model': UserSoilMoistureParameters,
            'form': UserSoilMoistureParametersForm,
            'modal_title': 'Modify Soil Moisture Parameters',
            'modal_save_button': 'Save Soil Moisture Parameters',
            'modal_save_as_button': 'Save as New Soil Moisture Parameters',
        },
        'soil-organic-parameters': {
            'model': UserSoilOrganicParameters,
            'form': UserSoilOrganicParametersForm,
            'modal_title': 'Modify Soil Organic Parameters',
            'modal_save_button': 'Save Soil Organic Parameters',
            'modal_save_as_button': 'Save as New Soil Organic Parameters',
        },
        'soil-temperature-parameters': {
            'model': SoilTemperatureModuleParameters,
            'form': SoilTemperatureModuleParametersForm,
            'modal_title': 'Modify Soil Temperature Parameters',
            'modal_save_button': 'Save Soil Temperature Parameters',
            'modal_save_as_button': 'Save as New Soil Temperature Parameters',
        },
        'soil-transport-parameters': {
            'model': UserSoilTransportParameters,
            'form': UserSoilTransportParametersForm,
            'modal_title': 'Modify Soil Transport Parameters',
            'modal_save_button': 'Save Soil Transport Parameters',
            'modal_save_as_button': 'Save as New Soil Transport Parameters',
        }
    }

    user = request.user

    

    if parameter not in MODEL_FORM_MAPPING:
        return JsonResponse({'message': {'success': False, 'errors': 'Invalid model name'}})
    
    model_info = MODEL_FORM_MAPPING[parameter]
    model_class = model_info['model']
    form_class = model_info['form']

    # TODO  check this part: why should this only apply to residue and not also to cultivar? What if request.POST
    if parameter == 'crop-residue-parameters':
        obj = get_object_or_404(model_class, species_parameters=id)
    else:
        obj = get_object_or_404(model_class, pk=id)


    if request.method == 'POST':
        print("Request POST: ", request.POST)
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            if request.POST.get('modal_action') == 'save_as_new':
                print("save as new is True")
                
                if instance.name == '':
                    base_name = f'{parameter} (copy)'
                else:
                    base_name = instance.name

                # Check if the name already exists;
                # Q is necesssary to allow for the OR condition/ the query for None
                existing_names = list(model_class.objects.filter(Q(user=None) | Q(user=user)).values_list('name', flat=True))
                print("existing names: ", existing_names)

                new_name = base_name
                while new_name in existing_names:
                    new_name = f'{new_name} (copy)'
                    
                    
                instance.name = new_name  

                instance.is_default = False
                instance.pk = None
                instance.user = request.user 
            
                instance.save()
                return JsonResponse({'message': {'success': True, 'message': 'New instance created.'},  'new_id': instance.pk})

            elif request.POST.get('modal_action') == 'delete' and instance.is_default is False:
                print("DELETE")
                instance.delete()
                return JsonResponse({'message': {'success': True, 'message': 'Instance deleted.'}})
            elif request.POST.get('modal_action') == 'save':
                print("SAVE")
                if instance.is_default:
                    return JsonResponse({'message': {'success': False, 'errors': 'Cannot modify the default species parameters. Please use save as new.'}})
                instance.save()
                return JsonResponse({'message': {'success': True, 'message': 'Parameters saved successfully.'}, 'new_id': instance.pk})
            else:
                print("WARNING: Something is wrong with modal action!!")

            
        else:
            return JsonResponse({'message': {'success': False, 'errors': form.errors}})
    else:


        form = form_class(instance=obj)
        data_action_url = f'{parameter}/{id}/'
        if rotation is not None:
            print('if rotation')
            data_action_url = f'{data_action_url}{rotation}/'
        print("Data action URL: ", data_action_url)
        context = {
            'form': form,
            'modal_title': model_info['modal_title'],
            'modal_save_button': model_info['modal_save_button'],
            'modal_save_as_button': model_info['modal_save_as_button'],
            'parameter_name': parameter,
            'parameter_id': id,
            'data_action_url': data_action_url,
            'rotation_index': rotation,
            'is_default': obj.is_default,
        }
        return render(request, 'monica/modify_parameters_modal.html', context)
    
# @login_required
def monica_model(request):
    """
    Sets up the GUI with all forms and data required for the MONICA model.
    This view is used for the MONICA page and also the SpreeWasser:N page.
    """
    user = request.user

    project_select_form = MonicaProjectSelectionForm(user=user)
    project_form = MonicaProjectForm(user=user)
    project_modal_title = 'Create new project'

    coordinate_form = CoordinateForm()
   
    workstep_selector_form =  WorkstepSelectorForm()
    workstep_sowing_form = WorkstepSowingForm(user=user)
    workstep_harvest_form = WorkstepHarvestForm()
    workstep_tillage_form = WorkstepTillageForm()
    workstep_irrigation_form = WorkstepIrrigationForm()
    workstep_mineral_fertilisation_form = WorkstepMineralFertilisationForm()
    workstep_organic_fertilisation_form = WorkstepOrganicFertilisationForm()

    # sim_settings_queryset = m_models.UserSimulationSettings.objects.filter(user__in=[user, None])
    user_simulation_settings = m_models.UserSimulationSettings.objects.get(is_default=True)
    user_simulation_settings_form = UserSimulationSettingsForm(instance=user_simulation_settings)

    user_simulation_settings_select_form = UserSimulationSettingsInstanceSelectionForm(user=user)

    user_crop_parameters_select_form = UserCropParametersSelectionForm(user=user)
    user_crop_parameters_form = UserCropParametersForm()

    user_environment_parameters_select_form = UserEnvironmentParametersSelectionForm(user=user)
    user_environment_parameters_form = UserEnvironmentParametersForm()

    user_soil_moisture_select_form = UserSoilMoistureInstanceSelectionForm(user=user)
    user_soil_organic_select_form = UserSoilOrganicInstanceSelectionForm(user=user)
    soil_temperature_module_select_form = SoilTemperatureModuleInstanceSelectionForm(user=user)
    user_soil_transport_parameters_select_form = UserSoilTransportParametersInstanceSelectionForm(user=user)

    # TODO delete this part
    ## POST LOGIC
    if request.method == 'POST':
        print("Request POST: ", request.POST)
        if 'save_simulation_settings' in request.POST or 'save_as_simulation_settings' in request.POST:
            user_simulation_settings_form = UserSimulationSettingsForm(request.POST)
            if user_simulation_settings_form.is_valid():
                
                if 'save_simulation_settings' in request.POST:
                    if user_simulation_settings.name == 'default' and user_simulation_settings.default and user_simulation_settings.user is None:
                        messages.error(request, "Cannot modify the default settings.")
                    else:
                        # Update existing settings
                        simulation_settings_instance = UserSimulationSettings.objects.get(id=request.POST.get('id'))
                        for field in user_simulation_settings_form.cleaned_data:
                            setattr(user_simulation_settings, field, user_simulation_settings_form.cleaned_data[field])
                        simulation_settings_instance.save()
                        messages.success(request, "Settings updated successfully.")
                elif 'save_as_simulation_settings' in request.POST:
                    # Save as new settings
                    new_name = request.POST.get('new_name')
                    if new_name:
                        new_settings = user_simulation_settings_form.save(commit=False)
                        new_settings.name = new_name
                        new_settings.user = request.user
                        new_settings.save()
                        messages.success(request, "Settings saved as new successfully.")
                    else:
                        messages.error(request, "Please provide a new name for the settings.")
            else:
                messages.error(request, "There was an error with the form.")

    context = {
        'project_select_form': project_select_form,
        'project_form': project_form,
        'project_modal_title': project_modal_title,
        'coordinate_form': coordinate_form,
        'user_crop_parameters_select_form': user_crop_parameters_select_form,
        'user_crop_parameters_form': user_crop_parameters_form,
        'user_simulation_settings_select_form': user_simulation_settings_select_form,
        'simulation_settings_form': user_simulation_settings_form,
        'user_environment_parameters_select_form': user_environment_parameters_select_form,
        'user_environment_parameters_form': user_environment_parameters_form,

        'workstep_selector_form': workstep_selector_form,
        'workstep_sowing_form': workstep_sowing_form,
        'workstep_harvest_form': workstep_harvest_form,
        'workstep_tillage_form': workstep_tillage_form,
        'workstep_mineral_fertilisation_form': workstep_mineral_fertilisation_form,
        'workstep_organic_fertilisation_form': workstep_organic_fertilisation_form,
        'workstep_irrigation_form': workstep_irrigation_form,


        'user_soil_moisture_select_form': user_soil_moisture_select_form,
        'user_soil_organic_select_form': user_soil_organic_select_form,
        'soil_temperature_module_selection_form': soil_temperature_module_select_form, 
        'user_soil_transport_parameters_selection_form': user_soil_transport_parameters_select_form,
    }
    return render(request, 'monica/monica_model.html', context)


def get_soil_parameters(request, lat, lon):
    """
    The view returns two profiles in cases where the profile has to be completed.
    It is used in the soil tab of MONICA/swn-Monica.
    """
    soil_profile = get_soil_profile('general', lat, lon)
    
    show_original_table = (soil_profile['SoilProfileParameters'] != soil_profile['OriginalSoilProfileParameters'])

    for hor in soil_profile['SoilProfileParameters']:
        i = 0
        for key, value in hor.items():
            if isinstance(value, list):
                # print(type(value), ''.join(str(value)))
                hor[key] = ''.join(map(str, value))
                
        i += 1
    for hor in soil_profile['OriginalSoilProfileParameters']:
        for key, value in hor.items():
            if isinstance(value, list):
                hor[key] = ''.join(map(str, value))
    # soil_profile = 
    
    context = {
        'modal_title': 'Soil Profile',
        'soil_profile': soil_profile,
        'show_original_table': show_original_table,
        }
    
    print("Soil Profile: ", soil_profile)
    return render(request, 'monica/soil_profile_modal.html', context)


def soil_profiles_from_polygon_ids(soil_profile_polygon_ids):
    """
    Get soil profiles from polygon ids.
    """
    unique_land_usages = buek_models.SoilProfile.objects.filter(
        polygon_id__in=soil_profile_polygon_ids
    ).values_list('landusage_corine_code', 'landusage').distinct()
    # Filter out water (code 51)
    land_usage_choices = {code: usage for code, usage in unique_land_usages if code != 51}
    
    # Initialize data_json with land usage codes
    data_json = {code: {} for code in land_usage_choices.keys()}

    soil_data = buek_models.SoilProfileHorizon.objects.select_related('soilprofile').filter(
        soilprofile__polygon_id__in=soil_profile_polygon_ids
        ).order_by('soilprofile__landusage_corine_code', 'soilprofile__system_unit', 'soilprofile__area_percentage', 'horizont_nr')

    # Loop through soil data and populate data_json
    
    for item in soil_data:
        try:
            if item.soilprofile.landusage_corine_code != 51:
                land_code = item.soilprofile.landusage_corine_code
                system_unit = item.soilprofile.system_unit
                area_percentage = item.soilprofile.area_percentage
                profile_id = item.soilprofile.id
                horizon_nr = item.horizont_nr

                if system_unit not in data_json[land_code]:
                    data_json[land_code][system_unit] = {
                        'area_percentages': set(),
                        'soil_profiles': {}
                    }

                data_json[land_code][system_unit]['area_percentages'].add(area_percentage)

                if area_percentage not in data_json[land_code][system_unit]['soil_profiles']:
                    data_json[land_code][system_unit]['soil_profiles'][area_percentage] = {}

                if profile_id not in data_json[land_code][system_unit]['soil_profiles'][area_percentage]:
                    data_json[land_code][system_unit]['soil_profiles'][area_percentage][profile_id] = {'horizons': {}}

                data_json[land_code][system_unit]['soil_profiles'][area_percentage][profile_id]['horizons'][horizon_nr] = {
                    'obergrenze_m': item.obergrenze_m,
                    'untergrenze_m': item.untergrenze_m,
                    'stratigraphie': item.stratigraphie,
                    'herkunft': item.herkunft,
                    'geogenese': item.geogenese,
                    # 'fraktion': item.fraktion,
                    'summe': item.summe,
                    # 'gefuege': item.gefuege,
                    # 'torfarten': item.torfarten,
                    # 'substanzvolumen': item.substanzvolumen,
                    'bulk_density_class': item.bulk_density_class.bulk_density_class if item.bulk_density_class_id is not None else 'no data',
                    'bulk_density': item.bulk_density_class.raw_density_g_per_cm3 if item.bulk_density_class_id is not None else 'no data',
                    'humus_class': item.humus_class.humus_class if item.humus_class_id is not None else 'no data',
                    'humus_corg': item.humus_class.corg if item.humus_class_id is not None else 'no data',
                    'ka5_texture_class': item.ka5_texture_class.ka5_soiltype if item.ka5_texture_class_id is not None else 'no data',
                    'sand': item.ka5_texture_class.sand if item.ka5_texture_class_id is not None else 'no data',
                    'clay': item.ka5_texture_class.clay if item.ka5_texture_class_id is not None else 'no data',
                    'silt': item.ka5_texture_class.silt if item.ka5_texture_class_id is not None else 'no data',
                    'ph_class': item.ph_class.ph_class if item.ph_class_id is not None else 'no data',
                    'ph_lower_value': item.ph_class.ph_lower_value if item.ph_class_id is not None else 'no data',
                    'ph_upper_value': item.ph_class.ph_upper_value if item.ph_class_id is not None else 'no data',                    
                }
        except Exception as e:
            print("Exception occurred:", e)
           
    # Sort area percentages
    for land_code in data_json:
        for system_unit in data_json[land_code]:
            data_json[land_code][system_unit]['area_percentages'] = sorted(list(data_json[land_code][system_unit]['area_percentages']))

    data_menu = {
        # 'soil_profile_form': forms.SoilProfileSelectionForm().set_choices(land_usage_choices),
        'text': 'name',
        'id': 1,
        'polygon_ids': soil_profile_polygon_ids,
        'system_unit_json': json.dumps(data_json),
        'landusage_choices': json.dumps(land_usage_choices),
    }
    
    return data_menu


def manual_soil_selection(request, lat, lon):
    print("manual soil selection ", lat, lon)
    

    start_time = time.time()

    polygon_ids = [buek_models.Buek200.get_polygon_id_by_lat_lon(float(lat), float(lon))]
    # user_field = models.UserField.objects.get(id=user_field_id)
    # name = user_field.name
    # soil_profile_polygon_ids = user_field.soil_profile_polygon_ids['buek_polygon_ids']
    
    # Retrieve unique land usage choices
    
    data_menu = soil_profiles_from_polygon_ids(polygon_ids)
    data_menu['id'] = 1
    data_menu['text'] = 'name'

    print('elapsed_time for soil json', (start_time - time.time()), ' seconds')
    # return render(request, 'monica/modal_manual_soil_selection.html', data_menu)
    return JsonResponse(data_menu)


    
def create_irrigation_envs(envs, data):
    """
    This function creates a new environment for each irrigation event.
    """
    today = datetime.strptime(data.get('todaysDate').split('T')[0], '%Y-%m-%d')
    # irrigations = [(3, 10.0), (3, 20.0), (6, 10.0), (6, 20.0), (9, 30.0)]
    irrigations = [ (6, 10.0), (6, 20.0), (9, 30.0)]
    for days, amount in irrigations:
        date = copy.deepcopy(today)
        env2 = copy.deepcopy(envs[0])
        worksteps = env2['cropRotation'][-1].get('worksteps')
        while date <= datetime.strptime(data.get('endDate').split('T')[0], '%Y-%m-%d'):
            date += timedelta(days=days)
            worksteps.append({
                "type": "Irrigation",
                "date": date.strftime('%Y-%m-%d'),
                "amount": [amount, 'mm']
            })
        worksteps.sort(key=lambda x: x['date'])
        env2['cropRotation'][-1]['worksteps'] = worksteps
        envs.append(env2)
    return envs

def create_irrigation_envs2(envs, data):
    """
    This function creates a new environment for each irrigation event.
    """
    today = datetime.strptime(data.get('todaysDate').split('T')[0], '%Y-%m-%d')


    simulation_settings = [
        # UserSimulationSettings.objects.get(id=30).to_json(),
        UserSimulationSettings.objects.get(id=31).to_json(),
        UserSimulationSettings.objects.get(id=32).to_json()
    ]
    for sim in simulation_settings:
        sim["AutoIrrigationParams"]["startDate"] = today.strftime('%Y-%m-%d')
        env2 = copy.deepcopy(envs[0])
        env2["params"]["simulationParameters"] = sim
        envs.append(env2)

    return envs


def save_project(data, user):
    project_saved = False
    if data.get('project_id') is not None:
        project_id = data.get('project_id')
        project = MonicaProject.objects.get(id=project_id)
    else:
        project = MonicaProject()
    project.name = data.get('name')
    project.description = data.get('description')
    project.start_date = data.get('startDate')
    project.save()
    # model setup
    if data.get('monica_model_setup') is not None:
        model_setup_id = data.get('monica_model_setup')
        model_setup = models.ModelSetup.objects.get(id=model_setup_id)
    else:
        model_setup = models.ModelSetup()
        model_setup.user = user
        model_setup.is_default = False
        model_setup.name = data.get('model_setup_name')
        model_setup.user_crop_parameters = models.UserCropParameters.objects.get(pk=int(data.get('userCropParamters')))
        model_setup.user_environment_parameters = models.UserEnvironmentParameters.objects.get(pk=int(data.get('userEnvironmentParameters')))
        model_setup.user_soil_moisture_parameters = models.UserSoilMoistureParameters.objects.get(pk= int(data.get('userSoilMoistureParameters')))
        model_setup.user_soil_transport_parameters = models.UserSoilTransportParameters.objects.get(pk= int(data.get('userSoilTransportParameters')))
        model_setup.user_soil_organic_parameters = models.UserSoilOrganicParameters.objects.get(pk= int(data.get('userSoilOrganicParameters')))
        model_setup.user_soil_temperature_parameters = models.SoilTemperatureModuleParameters.objects.get(pk= int(data.get('userSoilTemperatureModuleParameters')))
        model_setup.simulation_parameters = models.UserSimulationSettings.objects.get(pk= int(data.get('userSimulationSettings')))
        
        model_setup.save()

    # no if for calculation - they cannot be changed TODO deleted maybe?
    calculation = models.MonicaCalculation()
    calculation.name = data.get('calculation_name')
    calculation.description = data.get('calculation_description')    
    # site data
    if data.get('site_id') is not None:
        site_id = data.get('site_id')
        site = models.MonicaSite.objects.get(id=site_id)
    else:
        site = models.MonicaSite()
        site.user = user
        site.name = data.get('field_name', None)
        site.latitude = data.get('latitude', None)
        site.longitude = data.get('longitude', None)
        # TODO implement following params
        site.altitude = data.get('altitude', 100)
        site.slope = data.get('slope', 0)
        site.n_deposition = data.get('n_deposition', 11)
        #TODO implement soil 
        site.save()
    

    return project_saved

def run_simulation(request):
    user = request.user

    start = datetime.now()
    if request.method == 'POST':
        # data is the project json
        data = json.loads(request.body)
        print("Saving Project\n", data)
        try:
            save_project(data, user)
        except:
            pass

        print("Simulation is starting...\n")
        
        
        env = create_monica_env_from_json(data)
        # # split function here --> if swn, then create irrigation
        envs = [env]
        
        if data.get('swn_forecast', False):
            envs = create_irrigation_envs2(envs, data)
        
  
        json_msgs = []
        i = 0
        for e in envs:
            i += 1
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)
            socket.connect("tcp://swn_monica:6666")
            # print("check 6")
            # print(env)
            socket.send_json(e)
            file_path = Path(__file__).resolve().parent
            with open(f'{file_path}/monica_io/env_{str(i)}.json', 'w') as _: 
                json.dump(e, _)
            msg = run_consumer()
            # print("check 9: consumer run")
            json_msg = msg_to_json(msg)
            json_msgs.append(json_msg)
            # print("check 10: ")
            # print(msg)
            with open(f'{file_path}/monica_io/message_out_{str(i)}.json', 'w') as _: 
                json.dump(msg, _)
            with open(f'{file_path}/monica_io/json_message_out_{str(i)}.json', 'w') as _: 
                json.dump(json_msg, _)

        time_el = datetime.now() - start
        # print("Simulation is done.", len(envs), len(json_msgs), 'time elapsed: ', time_el)
        print("Simulation is done.", 'time elapsed: ', time_el)
        return JsonResponse({'message': {'success': True, 'message': json_msgs}})
    else:
        return JsonResponse({'message': {'success': False, 'message': 'Simulation not started.'}})

