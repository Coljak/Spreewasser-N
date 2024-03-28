#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import json
import csv
import sys
import zmq
import os
import app.swn.monica_io3 as monica_io3
import errno

#print(sys.path)

#print("pyzmq version: ", zmq.pyzmq_version(), " zmq version: ", zmq.zmq_version())


def run_producer(server = {"server": None, "port": None}, shared_id = None):

    context = zmq.Context()
    socket = context.socket(zmq.PUSH) # pylint: disable=no-member

    config = {
        "port": server["port"] if server["port"] else "6666",
        "server": server["server"] if server["server"] else "localhost",
        "sim.json": 'sim-min.json',
        "crop.json": 'crop-min.json',
        "site.json": 'site-min.json',
        "climate.csv": 'climate-min.csv',
        "debugout": "debug_out",
        "writenv": True,
        "shared_id": shared_id 
    }
    # read commandline args only if script is invoked directly from commandline
    if len(sys.argv) > 1 and __name__ == "__main__":
        for arg in sys.argv[1:]:
            k, v = arg.split("=")
            if k in config:
                if k == "writenv" :
                    config[k] = bool(v)
                else :
                    config[k] = v

    # print("producer config:", config)
    
    socket.connect("tcp://" + config["server"] + ":" + config["port"])

    with open(config["sim.json"]) as _:
        sim_json = json.load(_)
        print("\nsim_json\n", sim_json)

    with open(config["site.json"]) as _:
        site_json = json.load(_)
        print("\nsite_json\n", site_json)

    with open(config["crop.json"]) as _:
        crop_json = json.load(_)
        print("\ncrop_json\n", crop_json)

    climate_csv_json1 = {}
    climate_csv_json2 = {}
    # with open(config["climate.csv"]) as _:
    #     csv_reader = csv.DictReader(_)
    #     for idx, row in enumerate(csv_reader):
    #     # For format 1: Create a dictionary for each row with index as key
    #         climate_csv_json1[idx] = {key: row[key] for key in row}
        
    #         # For format 2: Populate dictionaries with lists
    #         if idx == 0:
    #             # Initialize lists for each key
    #             for key in row:
    #                 climate_csv_json2[key] = []

    #         # Append values to corresponding lists
    #         for key, value in row.items():
    #             climate_csv_json2[key].append(value)
            
    #     print("climate_csv_json1", climate_csv_json1)
    #     #print("climate_csv_json2", climate_csv_json2)

    env = monica_io3.create_env_json_from_json_config({
        "crop": crop_json,
        "site": site_json,
        "sim": sim_json,
        "climate": "" #climate_csv
    })
    env["csvViaHeaderOptions"] = sim_json["climate.csv-options"]
    env["pathToClimateCSV"] = config["climate.csv"]
    # print("pathToClimateCSV", env["pathToClimateCSV"])

    # add shared ID if env to be sent to routable monicas
    if config["shared_id"]:
        env["sharedId"] = config["shared_id"]

    if config["writenv"] :
        filename = os.path.join(os.path.dirname(__file__), config["debugout"], 'generated_env.json')
        print('filename: ', filename)
        WriteEnv(filename, env) 

    socket.send_json(env)

    print("done")

def WriteEnv(filename, env) :
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, 'w') as outfile:
        json.dump(env, outfile)

if __name__ == "__main__":
    run_producer()