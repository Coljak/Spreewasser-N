from . import models, forms
from swn import models as swn_models
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Transform

from .run_consumer_swn import run_consumer
from .run_producer import run_producer
from pathlib import Path
from . import monica_io3_swn
from .climate_data.lat_lon_mask import lat_lon_mask

from netCDF4 import Dataset, MFDataset
import numpy as np
from datetime import datetime, timedelta
from cftime import num2date, date2num, date2index

import pytz
import json
import zmq
import csv
import bisect
# create a new monica env
from . import climate
from .process_weather_data import *
from datetime import datetime, timedelta


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

def get_lat_lon_as_index(lat, lon):
    """
    Returns the index of the closest lat, lon to the given lat, lon in the netCDF grid
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


def get_climate_data_as_json(start_date, end_date, lat_idx, lon_idx):
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
    base_path = Path(__file__).resolve().parent
    climate_data_path = base_path.joinpath('climate_netcdf')
    for year in range(start_date.year, end_date.year + 1):
        for key, value in CLIMATE_VARIABLES.items():
            base_path = Path(__file__).resolve().parent
            file_path = f"{climate_data_path}/zalf_{value.lower()}_amber_{year}_v1-0.nc"
            nc = Dataset(file_path, 'r')
            start_idx = 0
            end_idx = len(nc['time'])
            if year == start_date.year:
                start_idx = date2index(start_date, nc['time'])
            elif year == end_date.year:
                end_idx = date2index(end_date, nc['time'])

            values = list(nc.variables[value][start_idx:end_idx, lat_idx, lon_idx])
           
            climate_json[key].extend(values)
            nc.close()
            print(year, value, key)
    print('Time elapsed in get_climate_data_as_json: ', datetime.now() - start)
    return climate_json

### MONICA VIEWS ###
def create_monica_env(
    species_id=30, 
    cultivar_id=4, 
    soil_profile_id=4174,
    start_date = datetime.strptime("2007-01-01", "%Y-%m-%d"),
    end_date = datetime.strptime("2007-12-31", "%Y-%m-%d"),
    lat_idx=200,
    lon_idx=200,
    lat = 52.8,
    lon = 13.8,
    slope = 0,
    height_nn = 0,
    n_deposition = 30):
    

    # temporary replacements from file crop_site_sim2.json until available from database 
    simj = {
        "debug?": True,
        "UseSecondaryYields": True,
        "NitrogenResponseOn": True,
        "WaterDeficitResponseOn": True,
        "EmergenceMoistureControlOn": True,
        "EmergenceFloodingControlOn": True,
        "UseNMinMineralFertilisingMethod": True,
        "NMinUserParams": {
        "min": 40,
        "max": 120,
        "delayInDays": 10
        },
        "NMinFertiliserPartition": models.MineralFertiliser.objects.get(id=3).to_json(),
        "JulianDayAutomaticFertilising": 89,
        "UseAutomaticIrrigation": False,
        "AutoIrrigationParams": {
        "irrigationParameters": {
            "nitrateConcentration": [
            0,
            "mg dm-3"
            ],
            "sulfateConcentration": [
            0,
            "mg dm-3"
            ]
        },
        "amount": [
            17,
            "mm"
        ],
        "threshold": 0.35
        }
    }
    
    cropRotation = [{
    "worksteps": [{
        "date": "0000-10-13",
        "type": "Sowing",
        "crop": {
        "is-winter-crop": True, # TODO is winter-crop is probably not required!!!
        "cropParams": {
            "species": {
            "=": models.SpeciesParameters.objects.get(id=species_id).to_json()
            },
            "cultivar": {
            "=": models.CultivarParameters.objects.get(id=cultivar_id).to_json()
            }
        },
        "residueParams": models.CropResidueParameters.objects.get(species_parameters=species_id).to_json()
        }
    }, {
        "type": "Harvest",
        "date": "0001-05-21"
    }]
    },
    ]
    cropRotations = None
    events = [
    "daily",
    [
        "Date",
        "Crop",
        "Stage",
        "ETa/ETc",
        "AbBiom",
        [
        "OrgBiom",
        "Leaf"
        ],
        [
        "OrgBiom",
        "Fruit"
        ],
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
    # end of replacement -------------------------------------------
    
    debugMode = True
    
    soil_horizons = swn_models.BuekSoilProfileHorizon.objects.filter(
    bueksoilprofile=soil_profile_id,   
    obergrenze_m__gte=0     
    ).order_by(
        'horizont_nr'           
    )
    soil_parameters = [horizon.to_json() for horizon in soil_horizons]
    
    siteParameters = {
        "Latitude": lat,
        "Slope": slope,
        "HeightNN": [
        height_nn,
        "m"
        ],
        "NDeposition": [
        n_deposition,
        "kg N ha-1 y-1"
        ],
        "SoilProfileParameters": soil_parameters
    }
    cpp = {
    "type": "CentralParameterProvider",
    "userCropParameters": models.UserCropParameters.objects.get(id=1).to_json(),
    "userEnvironmentParameters": models.UserEnvironmentParameters.objects.get(id=1).to_json(),
    "userSoilMoistureParameters": models.UserSoilMoistureParameters.objects.get(id=1).to_json(),
    "userSoilTemperatureParameters": models.SoilTemperatureModuleParameters.objects.get(id=1).to_json(),
    "userSoilTransportParameters": models.UserSoilTransportParameters.objects.get(id=1).to_json(),
    "userSoilOrganicParameters": models.UserSoilOrganicParameters.objects.get(id=1).to_json(),
    "simulationParameters": simj,
        "siteParameters": siteParameters
    }

    # values from the Hohenfinow example as test values. These values refer to the 'name' field in the db 
    user_environment_parameters_name = "default_environment" 
    
    
    # with open('/app/monica/climate_data/test_monica_climate.json', 'r') as json_file:
    #     available_climate_data = json.load(json_file)
    
    # print('available_climate_data', available_climate_data)
    print("check 1")
    available_climate_data = get_climate_data_as_json(start_date, end_date, lat_idx, lon_idx)
    print("check 2")
    climate_json =   {
        "type": "DataAccessor",
        "data": available_climate_data,
        "startDate": start_date,
        "endDate": end_date
      }
    print("check 3")
    env = {
        "type": "Env",
        "debugMode": debugMode,
        "params": cpp,
        "cropRotation": cropRotation,
        "cropRotations": cropRotations,
        "events": events,
        "climateData": climate_json
    }
    print("check 4")

    return env


def monica(request):
    return render(request, 'monica/monica_hohenfinow.html')


# TODO delete. This is for test purposes only
def monica_generate_hohenfinow(request):

    run_producer()
    msg = run_consumer()
    print('msg', msg["data"], "TYPE ", type(msg))
    return JsonResponse({'result': 'success', 'msg': msg})

# TODO delete. This is for test purposes only
def monica_generate_from_env_file(request):
    base_path = Path(__file__).resolve().parent.parent
    file_path = base_path.joinpath('swn/debug_out/generated_env_x_TEST_bu.json')
    with open(file_path, 'r') as f:
        # envj = f.read()
        envj = json.load(f)

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://swn_monica:6666")
    socket.send_json(envj)

    msg = run_consumer()
    return JsonResponse({'result': 'success', 'msg': msg})

# get options for cultivar parameters selectbox in monica_hohenfinow_db.html
def get_cultivar_parameters(request, id):       
    cultivars = models.CultivarParameters.objects.filter(species_parameters=id).order_by('cultivar_name')
    cultivar_list = []
    for cultivar in cultivars:
        if cultivar.cultivar_name != '':
            cultivar_list.append({
                'id': cultivar.id,
                'name': cultivar.cultivar_name,
            })
        else:
            cultivar_list.append({
                'id': cultivar.id,
                'name': 'default',
            })
    return JsonResponse({'cultivars': cultivar_list})
            
def monica_generate_hohenfinow_from_db(request):
    
    env = create_monica_env()
    # print('Type env', json.dumps(env))
    # print('env', env)
    file_path = Path(__file__).resolve().parent
    with open('env_from_db.json', 'w') as _: 
        json.dump(env, _)
    msg = run_consumer()
    msg = msg_to_json(msg)
    
    return JsonResponse({'result': 'success', 'msg': msg})

def monica_calc_w_params_from_db(request):
    start_time = datetime.now()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_field_id = data.get('userFieldId')
            species_id = data.get('speciesId')
            cultivar_id = data.get('cultivarId')
            soil_profile_id = data.get('soilProfileId')
            start_date_str = data.get('startDate')
            end_date_str = data.get('endDate')

            start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
            end_date = datetime.strptime(end_date_str, "%m/%d/%Y")   

            print("TRY TO GET WEATHER DATA: ", user_field_id)

            weather_coords = []
            print("Cherckpoint 0")
            if not swn_models.UserField.objects.get(id=user_field_id).weather_grid_points:
                weather_coords = json.loads(swn_models.UserField.objects.get(id=user_field_id).get_weather_grid_points())
            else:
                weather_coords = json.loads(swn_models.UserField.objects.get(id=user_field_id).weather_grid_points)
            

            envs = []
            for coord in weather_coords["weather_indices"]:
                lat = coord['lat']
                lon = coord['lon']
                lat_idx = coord['lat_idx']
                lon_idx = coord['lon_idx']
                if coord['is_valid']:
                    # climate_json = get_climate_data_as_json(start_date, end_date, lat_idx, lon_idx)   
                    envs.append(create_monica_env(species_id=species_id, cultivar_id=cultivar_id, soil_profile_id=soil_profile_id, start_date=start_date, end_date=end_date, lat_idx=lat_idx, lon_idx=lon_idx, lat=lat, lon=lon))                 
                else:
                    continue

            start_date_iso = start_date.date().isoformat()
            end_date_iso = end_date.date().isoformat()
            # env = create_monica_env(species_id=species_id, cultivar_id=cultivar_id, soil_profile_id=soil_profile_id, start_date=start_date_iso, end_date=end_date_iso)
            # print("STart_date ISO ", start_date_iso, "End_date ISO ", end_date_iso)
            # print('monica_calc_w_params_from_db\nspecies_id', species_id, 'cultivar_id', cultivar_id, 'soil_profile_id', soil_profile_id)
            
            msgs = []
            for env in envs:
                context = zmq.Context()
                socket = context.socket(zmq.PUSH)
                socket.connect("tcp://swn_monica:6666")
                socket.send_json(env)


                file_path = Path(__file__).resolve().parent
                with open('env_from_db.json', 'w') as _: 
                    json.dump(env, _)
                msg = run_consumer()
                msg = msg_to_json(msg)

                msgs.append(msg)

            end_time = datetime.now()
            print("Time elapsed in monica_calc: ",  end_time - start_time)
            return JsonResponse({'result': 'success', 'msg': msgs[0]})
        
        except Exception as e:
            print('Error', e)
            return JsonResponse({'result': 'error', 'msg': 'Invalid request'})
    
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


def msg_to_json(msg):
    """
    the json output of Monica is processed in this function so that every output 
    is a flat array with the length of the base array e.g. of dates for each output. 
    This is applied to all outputs such as 'daily', 'monthly, 'crop' etc."""
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


    print("msg_to_json")
    processed_msg = {}
    for_chart = {}
    for data_ in msg.get("data", []):
        results = data_.get("results", [])
        orig_spec = data_.get("origSpec", "")
        output_ids = data_.get("outputIds", [])

        orig_spec = orig_spec.replace("\"", "")
        
        for_chart[orig_spec] = {}
        for output_id, result_list in zip(output_ids, results):
            output_id["result"] = result_list
            try:
                output_id["jsonInput"] = json.loads(output_id["jsonInput"])
            except:
                pass
            
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


def get_site_params_height(polygon):
    polygon_25832 = Transform(polygon, srid=25832)

    dem_data_within_polygon = models.DigitalElevationModel.objects.filter(
        grid_file__intersects=polygon_25832
    )

    if dem_data_within_polygon.count() == 0:
        return None
    else:
        for dem in dem_data_within_polygon:
            print("DEM: ", dem)
            # dem_data = dem.grid_file.read()
            # dem_data = np.flipud(dem_data)
            # dem_data = np.ma.masked_where(dem_data == dem.nodata_value, dem_data)
            # dem_data = np.ma.masked_where(dem_data < 0, dem_data)
            # dem_data = np.ma.masked_where(dem_data > 1000, dem_data)
            # height = np.mean(dem_data)
            # return height