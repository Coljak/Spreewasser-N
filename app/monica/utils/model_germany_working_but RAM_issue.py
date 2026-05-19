from datetime import datetime, timedelta
import numpy as np
import os
import rasterio
import xarray as xr
from . import monica_constants, climate_store, monica_utils
from monica import models
from django.conf import settings
import buek.models as buek_models
from django.db.models import Q, Min, Max
import uuid

from queue import Queue
from threading import Thread
import dask.array as da
from netCDF4 import Dataset
import netCDF4 as nc4
import zmq
import uuid
import time
import copy
import pandas as pd


BATCH_SIZE = 150 # batches for monica runs, probably best between 100-300

# PARAMS = ["Yield", "LAI"] + [f"Mois_{i}" for i in range(1, 21)] + ["Mois_AVG"]
# EVENTS = [
#     "daily", ["Date", "Yield","LAI", "AbBiom", "PASW", ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ["Mois",[5, 9, "AVG"]], ["Mois",[1, 6, "AVG"]] ],
#     "monthly", ["Date","Yield","LAI", "AbBiom", "PASW", ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ["Mois",[5, 9, "AVG"]], ["Mois",[1, 6, "AVG"]]],
#     ]


###### IMPORTANT !!! Do not produce results that are nested lists. that happens for all non aggregated results that stem from layers (Mois, PASW, SOC). The reason is that the current frontend code is not able to handle nested lists and it would require a lot of changes to make it work. So please always produce flat lists, even for non-aggregated layer results. For example, for PASW, instead of producing a list of 10 values (one per layer), produce a list of 10 values with the same value (the non-aggregated value) for each layer. This way, the frontend can handle it without any changes. The same applies to Mois and SOC. For Mois, if it's not aggregated, produce a list of 20 values with the same value for each layer. For SOC, if it's not aggregated, produce a list of 3 values with the same value for each layer. Thank you! ######
EVENTS = [
    "daily", ["Date", "Yield", ["PASW", [1, 7, "AVG"]], ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]],],
    "monthly", ["Date", "Yield", ["PASW", [1, 7, "AVG"]], ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ],
    ]
SCENARIO = monica_constants.SCENARIOS[0]

def doy_to_iso(doy):
    if doy is None:
        return None
    date = datetime(2001, 1, 1) + timedelta(days=doy - 1)  # non-leap year
    # TODO: check if the first rotation is always 0000
    return f"0000-{date.strftime('%m-%d')}"


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


# def writer_worker(queue, nc_variables, metadata_variables):

#     while True:

#         batch_results = queue.get()

#         if batch_results is None:
#             queue.task_done()
#             break

#         for msg in batch_results:

#             custom_id = msg["customId"]

#             lat_idx = custom_id // 1000
#             lon_idx = custom_id % 1000

#             daily_block = next(
#                 d for d in msg["data"]
#                 if d["origSpec"] == '"daily"'
#             )

#             results = daily_block["results"]

#             # arr = np.asarray(results, dtype=np.float32).squeeze()
#             # block = np.array(results, dtype=np.float32)
#             # ds_block[:, lat_idx, lon_idx] = block

#             for meta in metadata_variables:

#                 var_name = meta["name_lower"]

#                 result_index = meta["result_index"]

#                 values = np.asarray(
#                     results[result_index],
#                     dtype=np.float32
#                 ).squeeze()

#                 nc_variables[var_name][:, lat_idx, lon_idx] = values

#         queue.task_done()




def run_monica_batch(envs, timeout_ms=20000):
    """
    Sends a batch of MONICA environments and collects results.

    :param envs: list of env dicts
    :param timeout_ms: receive timeout in milliseconds
    :return: dict {sharedId: msg}
    """
    start_time = datetime.now()
    if not envs:
        return {}

    context = zmq.Context()

    # --- producer (send jobs) ---
    producer = context.socket(zmq.PUSH)
    producer.connect("tcp://swn_monica:6666")

    # --- consumer (receive results) ---
    consumer = context.socket(zmq.DEALER)
    shared_id = str(uuid.uuid4())
    consumer.setsockopt_string(zmq.ROUTING_ID, shared_id)
    consumer.RCVTIMEO = timeout_ms
    consumer.connect("tcp://swn_monica:7777")

    results = []
    expected = len(envs)

    # --- SEND ALL ---
    id_map = {}  # customId -> env (optional, for debugging)

    for env in envs:
        env['sharedId'] = shared_id  # ensure sharedId is set
        producer.send_json(env)
        id_map[env["customId"]] = env

    # --- RECEIVE ALL ---
    received = 0
    start_time = datetime.now()

    while received < expected:
        print(f"[ZMQ] Waiting for messages... ({received}/{expected} received so far)")
        try:
            msg = consumer.recv_json()
            print('msg received with customId', msg.get("customId", 'no Custom Id!!'))
        except zmq.Again:
            # timeout
            print(f"[ZMQ] Timeout after receiving {received}/{expected} messages")
            break

        

        results.append(msg)
        received += 1
    print('got out of the loop, received', received, 'messages in total, expected was', expected)
    # --- CLEANUP ---
    producer.setsockopt(zmq.LINGER, 0)
    consumer.setsockopt(zmq.LINGER, 0)
    producer.close()
    print('Producer socket closed')
    consumer.close()
    print('Consumer socket closed')

    context.term()
    print('ZMQ context terminated')
    end_time = datetime.now() - start_time

    print('Batch processing time:', end_time)

    return results

LONG_NAMES_EN = {
    'Date': 'Date',
    'Yield': 'Yield',
    'Precip': 'Precipitation',
    'AbBiom': 'Above-ground Biomass',
    'OrgBiom': 'Organic Biomass',
    'PASW': 'Plant Available Soil Water',
    'SOC': 'Soil Organic Carbon',
    'Irrig': 'Irrigation',
    'LAI': 'Leaf Area Index',
    'Mois': 'Soil Moisture',
}

LONG_NAMES_DE = {
    'Date': 'Datum',
    'Yield': 'Ertrag',
    'Precip': 'Niederschlag',
    'AbBiom': 'Obere Biomasse',
    'OrgBiom': 'Organische Biomasse',
    'PASW': 'Pflanzenverfügbares Bodenwasser',
    'SOC': 'Bodenorganischer Kohlenstoff',
    'Irrig': 'Bewässerung',
    'LAI': 'Blattflächenindex',
    'Mois': 'Bodenfeuchtigkeit',
}


def parse_monica_metadata(sample_result):
    print(type(sample_result))
    print(sample_result)
    # customId = sample_result.get("customId", 0)
    # print("Parsing metadata from sample result, available keys:", customId)
    daily_meta = None
    monthly_meta = None
    long_names = LONG_NAMES_DE
    params = []
   


    for d in sample_result['data']:
        if d['origSpec'] in ['"daily"', '"monthly"']:
     

            data = {
                "dates": None,
                "variables": []
            }
            
            for i, oid in enumerate(d['outputIds']):
                if oid['name'] == "Date":
                    print(oid.keys(), "Date oid keys")
                    data['dates'] = np.array(
                        d['results'][i],
                        dtype='datetime64[D]'
                    )
                else:
                    longname = long_names.get(oid['name'], oid['name'])

                    metadata= {
                        'name_lower': oid['name'].lower(),
                        'name': oid['name'],
                        'fromLayer': oid.get('fromLayer', None),
                        'toLayer': oid.get('toLayer', None),
                        "displayName": oid.get('displayName', ''),
                        "fromLayer": oid.get('fromLayer', None),
                        "id": oid.get('id', None),
                        "jsonInput": oid.get('jsonInput', None),
                        "layerAggOp": oid.get('layerAggOp', None),
                        "name": oid.get('name', None),
                        "organ": oid.get('organ', None),
                        "timeAggOp": oid.get('timeAggOp', None),
                        "toLayer": oid.get('toLayer', None),
                        "type": oid.get('type', None),
                        "unit": oid.get('unit', None),    
                        'longname': longname,  
                        'result_index': i,
                    }

                    if oid['fromLayer'] != oid['toLayer'] and ("AVG" in oid['jsonInput'] or "SUM" in oid['jsonInput']):

                        aggregation_op = "AVG" if "AVG" in oid['jsonInput'] else "SUM"
                        
                        metadata['longname'] += f" {oid['fromLayer']*10}cm-{(oid['toLayer']+1)*10}cm"

                        metadata['layer_depth'] = f"_{aggregation_op.lower()}_{oid['fromLayer']*10}_{(oid['toLayer']+1)*10}"
                        metadata['name_lower']+=metadata['layer_depth']
                        metadata['is_layer_average'] = True
                    else:
                        metadata['is_layer_average'] = False
                        metadata['layer_depth'] = None

                    data['variables'].append(metadata)
                    params.append(metadata['name_lower'])
              
                
            if d['origSpec'] == '"daily"':
                daily_meta = data
            elif d['origSpec'] == '"monthly"':
                monthly_meta = data

    return daily_meta, monthly_meta


def writer_worker(queue, ds_daily, ds_monthly, daily_var_order, monthly_var_order):

    daily_var_index = {
        v: i for i, v in enumerate(daily_var_order)
    }

    monthly_var_index = {
        v: i for i, v in enumerate(monthly_var_order)
    }

    while True:

        batch_results = queue.get()

        if batch_results is None:
            queue.task_done()
            break

        # ---------------------------------------------------------
        # PROCESS COMPLETE BATCH IN MEMORY FIRST
        # ---------------------------------------------------------

        daily_pixel_data = []
        monthly_pixel_data = []

        for msg in batch_results:

            custom_id = msg["customId"]

            lat_idx = custom_id // 1000
            lon_idx = custom_id % 1000

            # ---------------- DAILY ----------------

            daily_block = next(
                d for d in msg["data"]
                if d["origSpec"] == '"daily"'
            )

            daily_arr = np.asarray(
                daily_block["results"][1:],   # skip dates
                dtype=np.float32
            ).T

            daily_pixel_data.append(
                (lat_idx, lon_idx, daily_arr)
            )

            # ---------------- MONTHLY ----------------

            monthly_block = next(
                d for d in msg["data"]
                if d["origSpec"] == '"monthly"'
            )

            monthly_arr = np.asarray(
                monthly_block["results"][1:],
                dtype=np.float32
            ).T

            monthly_pixel_data.append(
                (lat_idx, lon_idx, monthly_arr)
            )

        # ---------------------------------------------------------
        # WRITE DAILY
        # ---------------------------------------------------------

        for var_name, var_i in daily_var_index.items():

            da_var = ds_daily[var_name]

            for lat_idx, lon_idx, arr in daily_pixel_data:

                da_var[:, lat_idx, lon_idx] = arr[:, var_i]

        # ---------------------------------------------------------
        # WRITE MONTHLY
        # ---------------------------------------------------------

        for var_name, var_i in monthly_var_index.items():

            da_var = ds_monthly[var_name]

            for lat_idx, lon_idx, arr in monthly_pixel_data:

                da_var[:, lat_idx, lon_idx] = arr[:, var_i]

        queue.task_done()


def model_germany(scenario=SCENARIO):

    start = datetime.now()

    print("starting Germany forecast")

    germany_model_settings = models.GermanyModelParameters.objects.get(
        is_default=True
    )

    cpp = germany_model_settings.to_json()

    # ============================================================
    # STATIC DATA
    # ============================================================

    with rasterio.open(
        os.path.join(
            settings.MONICA_RASTER_DATA_DIR,
            'buek_id_agriculture_masked_4326.tif'
        )
    ) as ab:

        agri_buek_arr = ab.read(1)

        transform = ab.transform
        height = ab.height
        width = ab.width
        crs = ab.crs

    unique_buek_ids = np.unique(
        agri_buek_arr[agri_buek_arr != -9999]
    )

    soil_profiles = buek_models.SoilProfile.objects.filter(
        id__in=unique_buek_ids
    )

    soil_profile_dict = {
        sp.id: sp.get_monica_horizons_json()[0]
        for sp in soil_profiles
    }

    with rasterio.open(
        os.path.join(
            settings.MONICA_RASTER_DATA_DIR,
            'dgm200_4326_1000m.tif'
        )
    ) as alt:

        altitude_arr = alt.read(1)

    with rasterio.open(
        os.path.join(
            settings.MONICA_RASTER_DATA_DIR,
            'slope_percentage_4326_1000m.tif'
        )
    ) as s:

        slope_arr = s.read(1)

    with rasterio.open(
        os.path.join(
            settings.MONICA_RASTER_DATA_DIR,
            'nearest_station_per_cultivar',
            f'nearest_station_cultivar_{germany_model_settings.cultivar_name_for_sowing_dates}.tif'
        )
    ) as climate_stations_tif:

        climate_stations_arr = climate_stations_tif.read(1)

    stack = np.stack([
        agri_buek_arr.astype(float),
        altitude_arr.astype(float),
        slope_arr.astype(float),
        climate_stations_arr.astype(float)
    ])

    stack[stack == -9999] = np.nan

    # ============================================================
    # CLIMATE
    # ============================================================

    start_date = '2025-08-01'
    end_date = '2026-06-01'

    last_hindcast_date = climate_store.get_last_valid_hindcast_date()

    first_forecast_date = last_hindcast_date + timedelta(days=1)

    hindcast = climate_store.get_hindcast_subset(
        start_date,
        last_hindcast_date
    )

    forecast = climate_store.get_monica_forecast_subset(
        first_forecast_date,
        end_date,
        scenario
    )

    hindcast_np = {}
    forecast_np = {}

    for _, climate_var in monica_constants.CLIMATE_VARIABLES.items():

        hindcast_np[climate_var] = hindcast[climate_var].values
        forecast_np[climate_var] = forecast[climate_var].values

    # ============================================================
    # BUILD ENVS
    # ============================================================

    lat_lon_idx_dictionary = (
        models.DWDGridToPointIndices.get_lat_lon_dictionary()
    )

    forecast_lat_lon_idxs_dictionary = (
        models.DWDGridToPointIndices.get_forecast_lat_lon_dictionary()
    )

    cultivar = germany_model_settings.cultivar

    sowing_dates_list = models.SeedHarvestDates.objects.filter(
        cultivar_parameters=cultivar
    ).values(
        'climate_station__id',
        'avg_sowing_doy',
        'avg_harvest_doy'
    )

    sowing_dates_per_station = {
        data['climate_station__id']: {
            'sowing_date': doy_to_iso(data['avg_sowing_doy']),
            'harvest_date': doy_to_iso(data['avg_harvest_doy'])
        }
        for data in sowing_dates_list
    }

    workstep = {
        "date": "",
        "type": "Sowing",
        "crop": {
            "cropParams": {
                "species": {
                    "=": cultivar.species_parameters.to_json()
                },
                "cultivar": {
                    "=": cultivar.to_json()
                }
            },
            "residueParams":
                models.CropResidueParameters.objects.get(
                    species_parameters=cultivar.species_parameters,
                    is_default=True
                ).to_json()
        }
    }

    all_envs = []

    counter = 0



    for (f_lat, f_lon), lat_lon_list in (
        forecast_lat_lon_idxs_dictionary.items()
    ):
        
        # if counter == 50:       
        #     break

        
        counter += 1

        print(
            f'{counter} Processing forecast cell {(f_lat, f_lon)} '
            f'with {len(lat_lon_list)} points'
        )

        forecast_dict = {
            key: forecast_np[val][:, f_lat, f_lon]
            for key, val in monica_constants.CLIMATE_VARIABLES.items()
        }

        for (lat_idx, lon_idx) in lat_lon_list:

            cell = stack[:, lat_idx, lon_idx]

            if np.isnan(cell).any():
                continue

            climate_data = {
                key: np.concatenate([
                    hindcast_np[val][:, lat_idx, lon_idx],
                    forecast_dict[key]
                ]).tolist()
                for key, val in monica_constants.CLIMATE_VARIABLES.items()
            }

            buek_id = cell[0].astype(int)

            altitude = cell[1]
            slope = cell[2]
            station_id = cell[3].astype(int)

            indices_dict = lat_lon_idx_dictionary[lat_idx][lon_idx]
            

            monica_id = lat_idx * 1000 + lon_idx

            soil_profile = soil_profile_dict.get(
                buek_id,
                None
            )

            env_cpp = copy.deepcopy(cpp)

            env_cpp["siteParameters"] = {
                "Latitude": indices_dict['lat'],
                "Slope": slope,
                "HeightNN": [altitude, 'm'],
                "NDeposition": [10, 'kg N ha-1 y-1'],
                "SoilProfileParameters": soil_profile,
            }

            dates = sowing_dates_per_station[station_id]

            ws = copy.deepcopy(workstep)

            ws['date'] = dates['sowing_date']

            env = {
                "customId": monica_id,
                "type": "Env",
                "debugMode": False,
                "params": env_cpp,
                "cropRotation": [
                    {'worksteps': [ws]}
                ],
                "cropRotations": None,
                "events": EVENTS,
                "climateData": {
                    "type": "DataAccessor",
                    "data": climate_data,
                    "startDate": start_date,
                    "endDate": end_date,
                }
            }

            all_envs.append(env)

    print("Total envs:", len(all_envs))

    # ============================================================
    # METADATA
    # ============================================================
    print("Env", all_envs[0])

    sample_result = run_monica_batch([all_envs[0]])[0]

    daily_meta, monthly_meta = parse_monica_metadata(
        sample_result
    )

    daily_var_order = [
        m["name_lower"]
        for m in daily_meta["variables"]
    ]

    monthly_var_order = [
        m["name_lower"]
        for m in monthly_meta["variables"]
    ]

    daily_time_len = len(daily_meta["dates"])
    monthly_time_len = len(monthly_meta["dates"])

    lon = transform.c + (
        np.arange(width) + 0.5
    ) * transform.a

    lat = transform.f + (
        np.arange(height) + 0.5
    ) * transform.e

    # ============================================================
    # DAILY DATASET
    # ============================================================

    daily_data_vars = {}

    for meta in daily_meta["variables"]:

        var_name = meta["name_lower"]

        daily_data_vars[var_name] = (
            ("time", "y", "x"),
            da.full(
                (
                    daily_time_len,
                    height,
                    width
                ),
                np.nan,
                chunks=(1, 256, 256),
                dtype=np.float32
            ),
            {
                "long_name": meta["longname"],
                "units": meta.get("unit", "")
            }
        )

    ds_daily = xr.Dataset(
        data_vars=daily_data_vars,
        coords={
            "time": daily_meta["dates"],
            "y": np.arange(height),
            "x": np.arange(width),
            "lat": ("y", lat),
            "lon": ("x", lon),
        }
    )

    # ============================================================
    # MONTHLY DATASET
    # ============================================================

    monthly_data_vars = {}

    for meta in monthly_meta["variables"]:

        var_name = meta["name_lower"]

        monthly_data_vars[var_name] = (
            ("time", "y", "x"),
            da.full(
                (
                    monthly_time_len,
                    height,
                    width
                ),
                np.nan,
                chunks=(1, 256, 256),
                dtype=np.float32
            ),
            {
                "long_name": meta["longname"],
                "units": meta.get("unit", "")
            }
        )

    ds_monthly = xr.Dataset(
        data_vars=monthly_data_vars,
        coords={
            "time": monthly_meta["dates"],
            "y": np.arange(height),
            "x": np.arange(width),
            "lat": ("y", lat),
            "lon": ("x", lon),
        }
    )

    # ============================================================
    # WRITER THREAD
    # ============================================================

    q = Queue(maxsize=5)

    writer = Thread(
        target=writer_worker,
        args=(
            q,
            ds_daily,
            ds_monthly,
            daily_var_order,
            monthly_var_order
        )
    )

    writer.start()

    # ============================================================
    # RUN BATCHES
    # ============================================================

    for batch in chunked(all_envs, BATCH_SIZE):

        results = run_monica_batch(batch)

        q.put(results)

    q.put(None)

    writer.join()

    # ============================================================
    # SAVE
    # ============================================================

    daily_path = (
        "/app_data/monica/germany/monica_daily.nc"
    )

    monthly_path = (
        "/app_data/monica/germany/monica_monthly.nc"
    )

    encoding = {
        var: {
            "zlib": True,
            "complevel": 4,
            "dtype": "float32",
            "_FillValue": np.nan,
            "chunksizes": (1, 256, 256),
        }
        for var in ds_daily.data_vars
    }

    ds_daily.to_netcdf(
        daily_path,
        engine="netcdf4",
        encoding=encoding
    )

    ds_monthly.to_netcdf(
        monthly_path,
        engine="netcdf4",
        encoding=encoding
    )

    ds_daily.close()
    ds_monthly.close()

    print(
        "Complete model run done in",
        datetime.now() - start
    )


