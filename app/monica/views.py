from . import models
import json
import zmq
# create a new monica env
from . import climate
from pathlib import Path

### MONICA VIEWS ###
def create_monica_env():
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
        
    cropRotation = {
        "worksteps": [{
            "date": "0000-10-13",
            "type": "Sowing",
            "crop": {
                "is-winter-crop": True, # TODO is winter-crop is probably not required!!!
                "cropParams": {
                    "species": {
                        "=": models.SpeciesParameters.objects.get(id=37).to_json()
                    },
                    "cultivar": {
                        "=": models.CultivarParameters.objects.get(id=11).to_json()
                    }
                },
                "residueParams": models.CropResidueParameters.objects.get(id=97).to_json()
            }
        }, {
            "type": "Harvest",
            "date": "0001-05-21"
        }]
    }
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
                    3
                ]
            ],
            [
                "Mois",
                [
                    1,
                    3,
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
    type = "Env"
    debugMode = True
    siteParameters = {
            "Latitude": 52.8,
            "Slope": 0,
            "HeightNN": [
                0,
                "m"
            ],
            "NDeposition": [
                30,
                "kg N ha-1 y-1"
            ],
            "SoilProfileParameters": [
                {
                    "Thickness": [
                        0.3,
                        "m"
                    ],
                    "SoilOrganicCarbon": [
                        0.8,
                        "%"
                    ],
                    "KA5TextureClass": "Sl2",
                    "SoilRawDensity": [
                        1446,
                        "kg m-3"
                    ]
                },
                {
                    "Thickness": 0.1,
                    "SoilOrganicCarbon": [
                        0.15,
                        "%"
                    ],
                    "KA5TextureClass": "Sl2",
                    "SoilRawDensity": [
                        1446,
                        "kg m-3"
                    ]
                },
                {
                    "Thickness": 1.6,
                    "SoilOrganicCarbon": [
                        0.05,
                        "%"
                    ],
                    "KA5TextureClass": "Sl2",
                    "SoilRawDensity": [
                        1446,
                        "kg m-3"
                    ]
                }
            ]
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


    env = {
        "type": type,
        "debugMode": debugMode,
        "params": cpp,
        "cropRotation": cropRotation,
        "cropRotations": cropRotations,
        "events": events,
        # "pathToClimateCSV": "",
        "csvViaHeaderOptions": {
            "no-of-climate-file-header-lines": 2,
            "csv-separator": ","
        },
        "climateCSV": climate.climate

    }

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://swn_monica:6666")
    socket.send_json(env)

    return env


def use_existing_env():
    base_path = Path(__file__).resolve().parent.parent
    file_path = base_path.joinpath('swn/debug_out/generated_env_x_TEST_bu.json')
    with open(file_path, 'r') as f:
        # envj = f.read()
        envj = json.load(f)
    print(envj.keys())

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://swn_monica:6666")
    socket.send_json(envj)

    return envj