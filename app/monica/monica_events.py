swn_events = [
        "daily",
        ["Date", "Yield","LAI", "Precip", "Irrig", 
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
            "Irrig",
            "SUM"
            ],
            [
            "Precip",
            "SUM"
            ]
        ]
    ]



events_hohenfinow = [
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

events_from_wiki =  [
    "daily", [
      "Date", "Crop", "TraDef", "Tra", "NDef", "HeatRed", "FrostRed", "OxRed",
      "Stage", "TempSum", "VernF", "DaylF",
      "IncRoot", "IncLeaf", "IncShoot", "IncFruit",
      "RelDev", "LT50", "AbBiom",
      ["OrgBiom", "Root"], ["OrgBiom", "Leaf"], ["OrgBiom", "Shoot"],
      ["OrgBiom", "Fruit"], ["OrgBiom", "Struct"], ["OrgBiom", "Sugar"],
      "Yield", "SumYield", "GroPhot", "NetPhot", "MaintR", "GrowthR",	"StomRes",
      "Height", "LAI", "RootDep", "EffRootDep", "TotBiomN", "AbBiomN", "SumNUp",
      "ActNup", "PotNup", "NFixed", "Target", "CritN", "AbBiomNc", "YieldNc",
      "Protein",
      "NPP", ["NPP", "Root"], ["NPP", "Leaf"], ["NPP", "Shoot"],
      ["NPP", "Fruit"], ["NPP", "Struct"], ["NPP", "Sugar"],
      "GPP",
      "Ra",
      ["Ra", "Root"], ["Ra", "Leaf"], ["Ra", "Shoot"], ["Ra", "Fruit"],
      ["Ra", "Struct"], ["Ra", "Sugar"],
      ["Mois", [1, 20]], "Precip", "Irrig", "Infilt", "Surface", "RunOff", "SnowD", "FrostD",
      "ThawD", ["PASW", [1, 20]], "SurfTemp", ["STemp", [1, 5]],
      "Act_Ev", "Act_ET", "ET0", "Kc", "AtmCO2", "Groundw", "Recharge", "NLeach",
      ["NO3", [1, 20]], ["Carb", 0], ["NH4", [1, 20]], ["NO2", [1, 4]],
      ["SOC", [1, 6]], ["SOC-X-Y", [1, 3, "SUM"]], ["SOC-X-Y", [1, 20, "SUM"]],
      ["AOMf", 1], ["AOMs", 1], ["SMBf", 1], ["SMBs", 1], ["SOMf", 1],
      ["SOMs", 1], ["CBal", 1], ["Nmin", [1, 3]], "NetNmin", "Denit", "N2O", "SoilpH",
      "NEP", "NEE", "Rh", "Tmin", "Tavg", "Tmax", "Wind", "Globrad", "Relhumid", "Sunhours",
      "NFert"
    ]
  ]