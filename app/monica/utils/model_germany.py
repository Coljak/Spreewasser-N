from datetime import datetime, timedelta
import json
import numpy as np
import os
import rasterio
import xarray as xr
from . import monica_constants, climate_store, monica_utils
from monica import models
from django.conf import settings
import buek.models as buek_models
import numpy as np


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


global SKIPPED_IDS_DAILY
SKIPPED_IDS_DAILY = set()
global SKIPPED_IDS_MONTHLY
SKIPPED_IDS_MONTHLY = set()

BATCH_SIZE = 150 # batches for monica runs, probably best between 100-300
CHUNK_SIZE = 256 # chunks the arrays, and defines the netCDF tilesize
SCENARIO = monica_constants.SCENARIOS[0]

# PARAMS = ["Yield", "LAI"] + [f"Mois_{i}" for i in range(1, 21)] + ["Mois_AVG"]
# EVENTS = [
#     "daily", ["Date", "Yield","LAI", "AbBiom", "PASW", ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ["Mois",[5, 9, "AVG"]], ["Mois",[1, 6, "AVG"]] ],
#     "monthly", ["Date","Yield","LAI", "AbBiom", "PASW", ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ["Mois",[5, 9, "AVG"]], ["Mois",[1, 6, "AVG"]]],


#     ]




# EVENTS = [
#     "daily", ["Date", "Yield", ["PASW", [1, 7, "AVG"]], ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]],],
#     "monthly", ["Date", "Yield", ["PASW", [1, 7, "AVG"]], ["Mois",[1, 3, "AVG"]], ["Mois",[4, 6, "AVG"]], ],
#     ]

###### IMPORTANT !!! Do not produce results that are nested lists. that happens for all non aggregated results that stem from layers (Mois, PASW, SOC). The reason is that the current frontend code is not able to handle nested lists and it would require a lot of changes to make it work. So please always produce flat lists, even for non-aggregated layer results. For example, for PASW, instead of producing a list of 10 values (one per layer), produce a list of 10 values with the same value (the non-aggregated value) for each layer. This way, the frontend can handle it without any changes. The same applies to Mois and SOC. For Mois, if it's not aggregated, produce a list of 20 values with the same value for each layer. For SOC, if it's not aggregated, produce a list of 3 values with the same value for each layer. Thank you! ######
EVENTS = [
    "daily", ["Date", "Yield", ["PASW", [1, 7, "AVG"]]],
    "monthly", ["Date", "Yield", ["PASW", [1, 7, "AVG"]],], 
    ]

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


def doy_to_iso(doy):
    if doy is None:
        return None
    date = datetime(2001, 1, 1) + timedelta(days=doy - 1)  # non-leap year
    # TODO: check if the first rotation is always 0000
    return f"0000-{date.strftime('%m-%d')}"


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def get_tile_key(lat_idx, lon_idx):

    tile_y = lat_idx // CHUNK_SIZE
    tile_x = lon_idx // CHUNK_SIZE

    return (tile_y, tile_x)

# ============================================================
# RUN MONICA BATCH
# SKIP HANGING PIXELS
# LOG FAILED PIXELS
# ============================================================

def run_monica_batch(
    envs,
    queue,
    timeout_ms=120000,   # 2 minutes without a message => stop batch
):
    start_time = datetime.now()

    if not envs:
        return []

    context = zmq.Context()

    producer = context.socket(zmq.PUSH)
    producer.connect("tcp://swn_monica:6666")

    consumer = context.socket(zmq.DEALER)

    shared_id = str(uuid.uuid4())

    consumer.setsockopt_string(
        zmq.ROUTING_ID,
        shared_id
    )

    consumer.RCVTIMEO = timeout_ms

    consumer.connect("tcp://swn_monica:7777")

    expected = len(envs)

    # --------------------------------------------------------
    # TRACK SENT IDS
    # --------------------------------------------------------

    sent_ids = set()

    for env in envs:

        env["sharedId"] = shared_id

        sent_ids.add(env["customId"])

        producer.send_json(env)

    # --------------------------------------------------------
    # RECEIVE
    # --------------------------------------------------------

    received_ids = set()

 
    poller = zmq.Poller()

    poller.register(
        consumer,
        zmq.POLLIN
    )

    last_message_time = time.time()

    while len(received_ids) < expected:

        print(
            f"[ZMQ] Waiting for messages... "
            f"({len(received_ids)}/{expected} received)"
        )

        socks = dict(
            poller.poll(5000)   # check every 5 sec
        )

        # --------------------------------------------------------
        # MESSAGE AVAILABLE
        # --------------------------------------------------------

        if consumer in socks:

            msg = consumer.recv_json()

            last_message_time = time.time()

            custom_id = msg.get("customId")

            if custom_id is None:

                print("[ZMQ] message without customId")

                continue

            if custom_id in received_ids:

                print(f"[ZMQ] duplicate result {custom_id}")

                continue

            received_ids.add(custom_id)

            print(
                "msg received with customId",
                custom_id
            )
            print(
                "[QUEUE] size before put:",
                queue.qsize()
            )

            queue.put(msg)

    # --------------------------------------------------------
    # NO MESSAGE
    # --------------------------------------------------------

        else:

            seconds_without_message = (
                time.time() - last_message_time
            )

            print(
                "[ZMQ] no message for",
                round(seconds_without_message, 1),
                "seconds"
            )

            if seconds_without_message > 120:

                print(
                    "[ZMQ] BATCH TIMEOUT"
                )

                break



    # --------------------------------------------------------
    # FIND FAILED PIXELS
    # --------------------------------------------------------

    missing_ids = sent_ids - received_ids

    if missing_ids:

        print("\n==============================")
        print("MISSING MONICA RESULTS")
        print("==============================")

        for mid in sorted(missing_ids):

            lat_idx = mid // 1000
            lon_idx = mid % 1000

            print(
                f"FAILED PIXEL "
                f"customId={mid} "
                f"lat_idx={lat_idx} "
                f"lon_idx={lon_idx}"
            )

        print("==============================\n")

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    producer.setsockopt(zmq.LINGER, 0)
    consumer.setsockopt(zmq.LINGER, 0)

    producer.close()
    consumer.close()

    context.term()

    print(
        "Batch processing time:",
        datetime.now() - start_time
    )

    return missing_ids


def run_monica_single(env):
    q = Queue(maxsize=1)

    run_monica_batch([env], q)

    # pull exactly one message from queue
    msg = q.get()
    print(type(msg), "msg type in run_monica_single")

    return msg




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


# ============================================================
# WRITER THREAD
# DIRECT NETCDF WRITING
# ============================================================

def writer_worker(
    queue,
    nc_daily_vars,
    nc_monthly_vars,
    daily_var_order,
    monthly_var_order,
    width,
    height,
    tile_size=CHUNK_SIZE,
    sync_every=50,
    tiles=None
):

    # =========================================================
    # VARIABLE INDEX MAPS
    # =========================================================

    daily_var_index = {
        v: i for i, v in enumerate(daily_var_order)
    }

    monthly_var_index = {
        v: i for i, v in enumerate(monthly_var_order)
    }

    # =========================================================
    # TILE BUFFERS
    # =========================================================

    daily_buffers = {}
    monthly_buffers = {}

    tile_counts = {}
    write_counter = 0

    # =========================================================
    # HELPERS
    # =========================================================

    def get_or_create_daily_tile(tile_key, time_len):
        
        if tile_key not in daily_buffers:

            daily_buffers[tile_key] = {
                var_name: np.full(
                    (
                        time_len,
                        tile_size,
                        tile_size
                    ),
                    np.nan,
                    dtype=np.float32
                )
                for var_name in daily_var_order
            }

            tile_counts[tile_key] = 0


        return daily_buffers[tile_key]

    def get_or_create_monthly_tile(tile_key, time_len):

        if tile_key not in monthly_buffers:

            monthly_buffers[tile_key] = {
                var_name: np.full(
                    (
                        time_len,
                        tile_size,
                        tile_size
                    ),
                    np.nan,
                    dtype=np.float32
                )
                for var_name in monthly_var_order
            }

        return monthly_buffers[tile_key]

    # =========================================================
    # FLUSH TILE
    # =========================================================

    def flush_tile(tile_key):
        print('flushing tile', tile_key)
        
        nonlocal write_counter

        tile_y, tile_x = tile_key

        y0 = tile_y * tile_size
        x0 = tile_x * tile_size

        y1 = min(y0 + tile_size, height)
        x1 = min(x0 + tile_size, width)

        local_h = y1 - y0
        local_w = x1 - x0
        print(f"[WRITER] flushing tile {tile_key} at y={y0}:{y1}, x={x0}:{x1}")
        # -----------------------------------------------------
        # DAILY
        # -----------------------------------------------------

        if tile_key in daily_buffers:

            for var_name, arr in daily_buffers[tile_key].items():

                nc_daily_vars[var_name][
                    :,
                    y0:y1,
                    x0:x1
                ] = arr[
                    :,
                    :local_h,
                    :local_w
                ]

            del daily_buffers[tile_key]

        # -----------------------------------------------------
        # MONTHLY
        # -----------------------------------------------------

        if tile_key in monthly_buffers:

            for var_name, arr in monthly_buffers[tile_key].items():

                nc_monthly_vars[var_name][
                    :,
                    y0:y1,
                    x0:x1
                ] = arr[
                    :,
                    :local_h,
                    :local_w
                ]

            del monthly_buffers[tile_key]

        write_counter += 1

        # -----------------------------------------------------
        # PERIODIC DISK FLUSH
        # -----------------------------------------------------

        tile_counts.pop(tile_key, None)

        if write_counter % sync_every == 0:
            print(f"[WRITER] syncing to disk after {write_counter} tile writes...")

            first_daily = next(iter(nc_daily_vars.values()))
            first_monthly = next(iter(nc_monthly_vars.values()))

            first_daily.group().sync()
            first_monthly.group().sync()

    # =========================================================
    # MAIN LOOP
    # =========================================================
    current_tile = None

    while True:

        msg = queue.get()

        # -----------------------------------------------------
        # FINAL FLUSH
        # -----------------------------------------------------

        if msg is None:
            print('message is none- flushing all remaining tiles and exiting')
            keys = set(list(daily_buffers.keys())).copy()
            for tile_key in keys:
                
                flush_tile(tile_key)

            queue.task_done()

            break

        custom_id = msg["customId"]

        lat_idx = custom_id // 1000
        lon_idx = custom_id % 1000

        tile_key = get_tile_key(
            lat_idx,
            lon_idx
        )

        if tile_key != current_tile:
            current_tile = tile_key

        local_y = lat_idx % tile_size
        local_x = lon_idx % tile_size


        # =====================================================
        # DAILY
        # =====================================================

        daily_block = next(
            (
                d for d in msg.get("data", [])
                if d.get("origSpec") == '"daily"'
            ),
            None
        )

        if daily_block is None:
            SKIPPED_IDS_DAILY.add(custom_id)
            with open("skipped_daily_ids.txt", "a") as f:
                f.write(f"{json.dumps(msg)}\n")
            print(
                f"[WRITER] missing daily block "
                f"customId={custom_id}"
            )
            queue.task_done()
            continue

        daily_results = []

        for r in daily_block["results"][1:]:

            if isinstance(r, list):
                daily_results.append(r)
            else:
                daily_results.append([r])

        daily_arr = np.asarray(
            daily_results,
            dtype=np.float32
        ).T

        daily_tile = get_or_create_daily_tile(
            tile_key,
            daily_arr.shape[0]
        )

        for var_name, i in daily_var_index.items():

            daily_tile[var_name][
                :,
                local_y,
                local_x
            ] = daily_arr[:, i]

        # =====================================================
        # MONTHLY
        # =====================================================

        monthly_block = next(
            (
                d for d in msg.get("data", [])
                if d.get("origSpec") == '"monthly"'
            ),
            None
        )

        if monthly_block is None:
            SKIPPED_IDS_MONTHLY.add(custom_id)
            print(
                f"[WRITER] missing monthly block "
                f"customId={custom_id}"
            )
            queue.task_done()
            continue
        monthly_results = []

        for r in monthly_block["results"][1:]:

            if isinstance(r, list):
                monthly_results.append(r)
            else:
                monthly_results.append([r])

        monthly_arr = np.asarray(
            monthly_results,
            dtype=np.float32
        ).T

        monthly_tile = get_or_create_monthly_tile(
            tile_key,
            monthly_arr.shape[0]
        )

        for var_name, i in monthly_var_index.items():

            monthly_tile[var_name][
                :,
                local_y,
                local_x
            ] = monthly_arr[:, i]

        if tiles.get(current_tile, None) is not None:
            tiles[current_tile].remove((lat_idx, lon_idx))
            if len(tiles[current_tile]) == 0:  # if the list is empty, all pixels of the tile have been written
                flush_tile(current_tile)
                print(f"[WRITER] tile {current_tile} done, all pixels written")
        queue.task_done()


def model_germany(scenario=SCENARIO):

    start = datetime.now()

    print("starting Germany forecast")
    chunksize = CHUNK_SIZE

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

        global WIDTH
        WIDTH = width

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

    # ==========================================================
    #  CREATE ENVS FOR ALL CELLS
    # ==========================================================

    all_envs = []
    tiles = {}

    counter = 0

    for (f_lat, f_lon), lat_lon_list in (forecast_lat_lon_idxs_dictionary.items()):
        
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

            # create a dict of all tiles with their lat_lon_list, so that they can be accessed by the writer thread
            tile_key = get_tile_key(
                lat_idx,
                lon_idx
            )
            if not tile_key in tiles:
                tiles[tile_key] = set()
            

            cell = stack[:, lat_idx, lon_idx]

            if np.isnan(cell).any():
                continue

            tiles[tile_key].add((lat_idx, lon_idx))

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

    # SORT THE ENVS BY TILES
    all_envs.sort(
        key=lambda e: (
            (e["customId"] // 1000) // chunksize,
            (e["customId"] % 1000) // chunksize
        )
    )

    # ============================================================
    # METADATA
    # ============================================================
    print("Env", all_envs[0])


    sample_result = run_monica_single(all_envs[0])

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



    # ============================================================
    # NETCDF CREATION
    # ============================================================
    daily_tmp_path = os.path.join(
        settings.MONICA_GERMANY_DATA_DIR,
        "germany_daily_tmp.nc"
    )
    daily_path = os.path.join(
        settings.MONICA_GERMANY_DATA_DIR,
        "germany_daily.nc"
    )
    monthly_tmp_path = os.path.join(
        settings.MONICA_GERMANY_DATA_DIR,
        "germany_monthly_tmp.nc"
    )
    monthly_path = os.path.join(
        settings.MONICA_GERMANY_DATA_DIR,
        "germany_monthly.nc"
     )
    os.remove(daily_tmp_path) if os.path.exists(daily_tmp_path) else None
    os.remove(monthly_tmp_path) if os.path.exists(monthly_tmp_path) else None

    daily_nc = Dataset(
        daily_tmp_path,
        "w",
        format="NETCDF4"
    )

    monthly_nc = Dataset(
        monthly_tmp_path,
        "w",
        format="NETCDF4"
    )

    daily_nc.createDimension(
        "time",
        len(daily_meta["dates"])
    )

    monthly_nc.createDimension(
        "time",
        len(monthly_meta["dates"])
    )

    for nc in [daily_nc, monthly_nc]:
        nc.createDimension("lat", height)
        nc.createDimension("lon", width)

    
    # ------------------------------------------------------------
    # COORDS
    # ------------------------------------------------------------

    def create_coords(nc, dates):

        time_var = nc.createVariable(
            "time",
            "i4",
            ("time",)
        )


        lat_var = nc.createVariable(
            "lat",
            "f4",
            ("lat",)
        )

        lon_var = nc.createVariable(
            "lon",
            "f4",
            ("lon",)
        )

        time_var.units = (
            f"days since {start_date}"
        )

        time_var.calendar = "standard"

        time_var[:] = nc4.date2num(
            pd.to_datetime(dates).to_pydatetime(),
            units=time_var.units,
            calendar=time_var.calendar
        )


        # ---------------------------------------------------------
        # geographic coordinates
        # ---------------------------------------------------------
        lon = transform.c + (
            np.arange(width) + 0.5
        ) * transform.a

        lat = transform.f + (
            np.arange(height) + 0.5
        ) * transform.e

        lat_var[:] = lat
        lon_var[:] = lon

        lat_var.standard_name = "latitude"
        lat_var.units = "degrees_north"
        lat_var.axis = "Y"

        lon_var.standard_name = "longitude"
        lon_var.units = "degrees_east"
        lon_var.axis = "X"


        # ---------------------------------------------------------
        # CRS
        # ---------------------------------------------------------
        crs_var = nc.createVariable(
            "crs", 
            "i4"
            )
        crs_var.spatial_ref = crs.to_wkt()
        crs_var.grid_mapping_name = "latitude_longitude"

        crs_var.crs_wkt = crs.to_wkt()

    create_coords(
        daily_nc,
        daily_meta["dates"]
    )

    create_coords(
        monthly_nc,
        monthly_meta["dates"]
    )

    # ============================================================
    # CREATE VARIABLES
    # ============================================================

    nc_daily_vars = {}
    

    for meta in daily_meta["variables"]:

        var_name = meta["name_lower"]

        var = daily_nc.createVariable(
            var_name,
            "f4",
            ("time", "lat", "lon"),
            fill_value=np.nan,
            chunksizes=(1, chunksize, chunksize),
            zlib=False,
            # complevel=4
        )

        var.long_name = meta["longname"]

        var.units = meta.get("unit", "")

        var.grid_mapping = "crs"
        var.coordinates = "lat lon"

        nc_daily_vars[var_name] = var


    nc_monthly_vars = {}

    for meta in monthly_meta["variables"]:

        var_name = meta["name_lower"]

        var = monthly_nc.createVariable(
            var_name,
            "f4",
            ("time", "lat", "lon"),
            fill_value=np.nan,
            chunksizes=(1, chunksize, chunksize),
            zlib=False,
            # complevel=4
        )

        var.long_name = meta["longname"]

        var.units = meta.get("unit", "")

        var.grid_mapping = "crs"
        var.coordinates = "lat lon"

        nc_monthly_vars[var_name] = var

    # ============================================================
    # START WRITER
    # ============================================================

    q = Queue(maxsize=10000)

    writer = Thread(
        target=writer_worker,
        args=(
            q,
            nc_daily_vars,
            nc_monthly_vars,
            daily_var_order,
            monthly_var_order,
            width,
            height,
            chunksize,   # tile size
            50,
            tiles   # sync every N tile writes
        )
    )

    writer.start()

    # ============================================================
    # RUN BATCHES
    # ============================================================
    failed_pixels = []
    i = 0
    for batch in chunked(all_envs, BATCH_SIZE):
        i +=1
        print('Batch no:', i, 'with batch size:', len(batch))
        missing_ids = run_monica_batch(
            batch,
            q
        )

        failed_pixels.extend(missing_ids)

    q.put(None)

    writer.join()

    # ============================================================
    # FINALIZE
    # ============================================================

    daily_nc.sync()
    monthly_nc.sync()

    daily_nc.close()
    monthly_nc.close()

    os.rename(daily_tmp_path, daily_path)
    os.rename(monthly_tmp_path, monthly_path)

    os.remove(daily_tmp_path) if os.path.exists(daily_tmp_path) else None
    os.remove(monthly_tmp_path) if os.path.exists(monthly_tmp_path) else None

    print("FAILED PIXELS TOTAL:", len(failed_pixels))

    if failed_pixels:

        failed_path = os.path.join(
            settings.MONICA_GERMANY_DATA_DIR,
            "failed_pixels.txt"
        )

        with open(failed_path, "w") as f:

            for mid in failed_pixels:

                lat_idx = mid // 1000
                lon_idx = mid % 1000

                f.write(
                    f"{mid},{lat_idx},{lon_idx}\n"
                )

        print("failed pixels written to", failed_path)
    print(
        "Complete model run done in",
        datetime.now() - start,
        "skipped daily blocks:", SKIPPED_IDS_DAILY,
        "skipped monthly blocks:", SKIPPED_IDS_MONTHLY
    )


