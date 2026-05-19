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
import zmq
import uuid
import time
import copy


BATCH_SIZE = 150 # batches for monica runs, probably best between 100-300

# PARAMS = ["Yield", "LAI"] + [f"Mois_{i}" for i in range(1, 21)] + ["Mois_AVG"]
EVENTS = [
    "daily", ["Date", "Yield","LAI", "AbBiom", "PASW", ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ["Mois",[5, 9, "AVG"]], ["Mois",[1, 6, "AVG"]] ],
    "monthly", ["Date","Yield","LAI", "AbBiom", "PASW", ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ["Mois",[5, 9, "AVG"]], ["Mois",[1, 6, "AVG"]]],
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


def writer_worker(queue, ds, metadata_variables):

    while True:

        batch_results = queue.get()

        if batch_results is None:
            break

        # batch_results is a LIST
        for msg in batch_results:

            custom_id = msg["customId"]

            lat_idx = custom_id // 1000
            lon_idx = custom_id % 1000

            # get daily block
            daily_block = next(
                d for d in msg["data"]
                if d["origSpec"] == '"daily"'
            )

            results = daily_block["results"]

            # loop over metadata definitions
            for meta in metadata_variables:

                var_name = meta["name_lower"]

                result_index = meta["result_index"]

                # values = results[result_index]
                values = np.asarray(results[result_index]).squeeze()

                ds[var_name][:, lat_idx, lon_idx] = values

        queue.task_done()




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

        custom_id = msg.get("customId", None)

        if custom_id is None:
            print("[ZMQ] Warning: message without customId")
            continue

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

                    if oid['fromLayer'] != oid['toLayer'] and "AVG" in oid['jsonInput']:
                        
                        metadata['longname'] += f" {oid['fromLayer']*10}cm-{(oid['toLayer']+1)*10}cm"

                        metadata['layer_depth'] = f"_avg_{oid['fromLayer']*10}_{(oid['toLayer']+1)*10}"
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


def model_germany(scenario=SCENARIO):

    start = datetime.now()
    print("starting Germany forecast")

    # --- LOAD STATIC DATA (unchanged) ---
    germany_model_settings = models.GermanyModelParameters.objects.get(is_default=True)
    cpp = germany_model_settings.to_json()

    with rasterio.open(os.path.join(settings.MONICA_RASTER_DATA_DIR, 'buek_id_agriculture_masked_4326.tif')) as ab:
        agri_buek_arr = ab.read(1)

        # metadat for netcdf creation
        transform = ab.transform
        height = ab.height
        width = ab.width
        crs = ab.crs
    unique_buek_ids = np.unique(agri_buek_arr[agri_buek_arr != -9999])
    soil_profiles = buek_models.SoilProfile.objects.filter(id__in=unique_buek_ids)
    soil_profile_dict = {sp.id: sp.get_monica_horizons_json()[0] for sp in soil_profiles}

    buek_time = datetime.now()
    print("Soil profiles loaded", buek_time - start)

    with rasterio.open(os.path.join(settings.MONICA_RASTER_DATA_DIR, 'dgm200_4326_1000m.tif')) as alt:
        altitude_arr = alt.read(1)

    with rasterio.open(os.path.join(settings.MONICA_RASTER_DATA_DIR, 'slope_percentage_4326_1000m.tif')) as s:
        slope_arr = s.read(1)

    with rasterio.open(os.path.join(settings.MONICA_RASTER_DATA_DIR, 'nearest_station_per_cultivar',
                                   f'nearest_station_cultivar_{germany_model_settings.cultivar_name_for_sowing_dates}.tif')) as climate_stations_tif:
        climate_stations_arr = climate_stations_tif.read(1)

    # clean NaNs

    stack = np.stack([
        agri_buek_arr.astype(float),
        altitude_arr.astype(float),
        slope_arr.astype(float),
        climate_stations_arr.astype(float)
    ])

    stack[stack == -9999] = np.nan

    

    stack_time = datetime.now()
    print("Raster data loaded and stacked", stack_time - buek_time)

    # --- CLIMATE ---
    start_date = '2025-08-01'
    end_date = '2026-06-01'

    last_hindcast_date = climate_store.get_last_valid_hindcast_date()
    first_forecast_date = last_hindcast_date + timedelta(days=1)

    hindcast = climate_store.get_hindcast_subset(start_date, last_hindcast_date)
    forecast = climate_store.get_monica_forecast_subset(first_forecast_date, end_date, scenario)


    # --- BUILD ALL ENVS FIRST ---


    hindcast_np = {}
    forecast_np = {}
    for _, climate_var in monica_constants.CLIMATE_VARIABLES.items():
        hindcast_np[climate_var] = hindcast[climate_var].values
        forecast_np[climate_var] = forecast[climate_var].values
    
    lat_lon_idx_dictionary = models.DWDGridToPointIndices.get_lat_lon_dictionary()
    forecast_lat_lon_idxs_dictionary = models.DWDGridToPointIndices.get_forecast_lat_lon_dictionary()

    cultivar = germany_model_settings.cultivar
    sowing_dates_list = models.SeedHarvestDates.objects.filter(cultivar_parameters=cultivar).values('climate_station__id', 'avg_sowing_doy', 'avg_harvest_doy')  
    sowing_dates_per_station = {data['climate_station__id']: {'sowing_date': doy_to_iso(data['avg_sowing_doy']), 'harvest_date': doy_to_iso(data['avg_harvest_doy'])} for data in sowing_dates_list}

    workstep = {
        "date":  '',               # "0000-10-13",
        "type": "Sowing",
        "crop": {
            # "is-winter-crop": True, # TODO is winter-crop is probably not required!!!
            "cropParams": {
                "species": {
                "=": cultivar.species_parameters.to_json()
                },
                "cultivar": {
                "=": cultivar.to_json()
                }
            },
            "residueParams": models.CropResidueParameters.objects.get(species_parameters=cultivar.species_parameters, is_default=True).to_json()
        }
    }

    all_envs = []
    skipped = []
    counter = 0

    prep_time = datetime.now()
    print("Preparation of envs started", prep_time - start)

    for (f_lat, f_lon), lat_lon_list in forecast_lat_lon_idxs_dictionary.items():
        print('start env creation')
        # if counter == 50:
        #     break
        counter += 1
        print(f'{counter} Processing forecast cell {(f_lat, f_lon)} with {len(lat_lon_list)} points')



        # --- Extract forecast ONCE ---
        forecast_dict = {
            key: forecast_np[val][:, f_lat, f_lon]  # keep as numpy array!
            for key, val in monica_constants.CLIMATE_VARIABLES.items()        }

        for (lat_idx, lon_idx) in lat_lon_list:
            cell = stack[:, lat_idx, lon_idx]
            if np.isnan(cell).any():
                skipped.append((lat_idx, lon_idx))
                # print(f'Skipping cell at lat_idx {lat_idx}, lon_idx {lon_idx} due to missing data')
                continue

            climate_data = {
                key: np.concatenate([
                    hindcast_np[val][:, lat_idx, lon_idx],
                    forecast_dict[key]  
                ]).tolist()  # convert to list for JSON serialization
                for key, val in monica_constants.CLIMATE_VARIABLES.items()
            }
            
            buek_id = cell[0].astype(int)
            altitude = cell[1]
            slope = cell[2]
            station_id = cell[3].astype(int)

            indices_dict = lat_lon_idx_dictionary[lat_idx][lon_idx]
            monica_id = lat_idx * 1000 + lon_idx

            soil_profile = soil_profile_dict.get(buek_id, None)

            env_cpp = copy.deepcopy(cpp)

            env_cpp["siteParameters"] = {
                "Latitude": indices_dict['lat'],
                "Slope": slope,
                "HeightNN": [altitude, 'm'],
                "NDeposition": [10, 'kg N ha-1 y-1'],
                "SoilProfileParameters": soil_profile,
            }
            
                
                # create env for MONICA
            dates = sowing_dates_per_station[station_id]
            ws = copy.deepcopy(workstep)
            ws['date'] = dates['sowing_date']

                
            env = {
                "customId": monica_id,
                "type": "Env",
                "debugMode": False,
                "params": env_cpp,
                "cropRotation": [
                    {'worksteps': [ws],}
                ],
                "cropRotations": None,
                "events": EVENTS,
                "climateData": {
                    "type": "DataAccessor",
                    "data":   climate_data,
                    "startDate": start_date,
                    "endDate": end_date,}
            }
            all_envs.append(env)

    env_time = datetime.now()
    print(f"Total envs: {len(all_envs)}, time taken for env preparation: {env_time - prep_time}")

    # create the output netcdf

    lon = transform.c + (np.arange(width) + 0.5) * transform.a
    lat = transform.f + (np.arange(height) + 0.5) * transform.e
    sample_result = run_monica_batch([all_envs[0]])[0] # returs list
    daily_meta, monthly_meta = parse_monica_metadata(sample_result)
    print("Metadata parsed from sample result:", daily_meta)


    time_len = len(daily_meta['dates'])
    shape = (time_len, height, width)

    ds = xr.Dataset(
        coords={
            "time": daily_meta["dates"],
            "y": np.arange(height),
            "x": np.arange(width),
            "lat": (("y"), lat),
            "lon": (("x"), lon),
        },
        attrs={
            "crs": str(crs),
            "transform": tuple(transform),
            "Conventions": "CF-1.8",
        }
    )
    

    for meta in daily_meta["variables"]:

        var_name = meta["name_lower"]

        ds[var_name] = xr.DataArray(
            da.full(shape, np.nan, dtype=np.float32, chunks=(time_len, 1, 1)),
            dims=("time", "y", "x"),
            attrs={
                "long_name": meta["longname"],
                "units": meta["unit"],
            }
        )

    encoding = {
        var: {
            "zlib": True,
            "complevel": 4,
            "dtype": "float32",
            "_FillValue": np.nan,
            "chunksizes": (time_len, 1, 1),
        }
        for var in ds.data_vars
    }
    # --- START WRITER THREAD ---
    q = Queue(maxsize=5)
    writer = Thread(target=writer_worker, args=(q, ds,  daily_meta['variables']))
    writer.start()

    # --- PROCESS IN BATCHES ---
    for batch in chunked(all_envs, BATCH_SIZE):
        results = run_monica_batch(batch)
        q.put(results)

    # --- FINALIZE ---
    q.put(None)
    writer.join()

    
    tmp_path = "/app_data/monica/germany/monica_results_tmp.nc"
    final_path = "/app_data/monica/germany/monica_results.nc"

    ds.to_netcdf(
        tmp_path,
        engine="netcdf4",
        encoding=encoding,
    )

    os.replace(tmp_path, final_path) 
    ds.close()

    print("Complete model run done in", datetime.now() - start)


