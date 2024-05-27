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
import zmq
import os
import errno
from datetime import datetime
from monica import models as monica_models
from swn import models as swn_models

from django.db.models import Q, F 
"""
Q: objects allow you to perform complex queries by combining multiple query 
expressions (such as filter(), exclude(), or annotate()) using logical operators 
like & (AND), | (OR), and ~ (NOT). They are useful for constructing complex 
queries with conditions involving multiple fields or relationships.

F: objects allow you to reference model field values directly within queries. 
They are useful for performing dynamic filtering or updating based on the 
values of other fields within the same model.
"""



def create_env():
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://swn_monica:6666")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug_out/generated_env_x_TEST.json')) as _:
        env = json.load(_)

    # for el in env["cropRotation"]:
    #     for ws in el["worksteps"]:
    #         if ws["type"] == "Sowing":
    #             obj= monica_models.SpeciesParameters.objects.get(id=29)
    #             obj_json = obj.to_json()
    #             ws["crop"]["cropParams"]["species"]["="] = obj_json
    #             print(ws["crop"]["cropParams"]["species"]["="])
    socket.send_json(env)



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

def create_site(soil_profile_id=10):
    print("CREATING SITE")
    soil_profile_horizons = swn_models.BuekSoilProfileHorizon.objects.filter(
        Q(obergrenze_m__gte=0, obergrenze_m__lt=2.0) &
        Q(bueksoilprofile_id=soil_profile_id)
    ).order_by('horizont_nr')

    latitude = 52.8
    slope = 0
    height_nn = 0 # in m
    n_deposition = 30 # kg N ha-1 y-1  TODO: where does the N deposition come from?
    thickness_1 = 0.3
    thickness_2 = 0.1
    thickness_3 = 1.6
    soc_1 = 0.8
    soc_2 = 0.15
    soc_3 = 0.05
    soil_raw_density_1 = 1446 # kg m-3
    soil_raw_density_2 = 1446 # kg m-3
    soil_raw_density_3 = 1446 # kg m-3
    site_parameters =  {
            "Latitude": latitude,
            "Slope": slope,
            "HeightNN": [
                height_nn,
                "m"
            ],
            "NDeposition": [
                n_deposition,
                "kg N ha-1 y-1"
            ],
            "SoilProfileParameters": [
                {
                    "Thickness": [
                        thickness_1,
                        "m"
                    ],
                    "SoilOrganicCarbon": [
                        soc_1,
                        "%"
                    ],
                    "KA5TextureClass": "Sl2",
                    "SoilRawDensity": [
                        soil_raw_density_1,
                        "kg m-3"
                    ]
                },
                {
                    "Thickness": thickness_2,
                    "SoilOrganicCarbon": [
                        soc_2,
                        "%"
                    ],
                    "KA5TextureClass": "Sl2",
                    "SoilRawDensity": [
                        soil_raw_density_2,
                        "kg m-3"
                    ]
                },
                {
                    "Thickness": thickness_3,
                    "SoilOrganicCarbon": [
                        soc_3,
                        "%"
                    ],
                    "KA5TextureClass": "Sl2",
                    "SoilRawDensity": [
                        soil_raw_density_3,
                        "kg m-3"
                    ]
                }
            ]
        }
    return site_parameters