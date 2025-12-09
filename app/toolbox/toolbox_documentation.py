"""
Docstring for app.toolbox.toolbox_documentation
The dictionary helptexts is used to store all helptexts for filters in toolbox.filters.py and forms in toolbox.forms.py.
The helptexts for tableheader are stored in the database: toolbox_datainfoproperty.help_text (model: DataInfoProperty, in js p.helpText).
"""


helptexts = {
    #### ZALF SINKS ####
    ### filter
    'zalf_sink': { # works for sinks and enlarged sinks
        'area': None,
        'volume': None,
        'depth': None,
        'land_use': '''
          Hier werden alle Landnutzungsarten ab 1% der Senkenfläche angezeigt. 
          Der Anteil der jeweiligen Flächennutzung ist im Ergebnis aufgeführt.
          ''',
        'volume_construction_barrier': None,
        'volume_gained': None,
                },
    'stream': { # same as lake
        'mean_surplus_volume': None,
        'plus_days': None,
        'distance_to_userfield': 'Hier können Sie den Suchradius um Ihr Suchgebiet erweitern.'
    },
    'InletWeightingsForm': {
        'weighting_inlet_length': 'Gewichtung der Länge der Zuleitung',
        'weighting_inlet_volume': 'Gewichtung des Verhältnisses ökologischer Mindestabflusses zu Senkenvolumen '
    },
    'OverallWeightingsForm': {
        'overall_usability': "Die allgemeine Nutzbarkeit ist eine Bewertung der Eignung des Standorts für Versickerungsmaßnahmen. Eine hohe Bewertung begünstigt Versickerungsmaßnahmen.",
        'soil_index':  None,
    },
    'WeightingsForestForm': {
        'field_capacity': 'Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt Versickerungsmaßnahmen.',
        'hydraulic_conductivity_1m': "Die hydraulische Leitfähigkeit ist die gesättigte Wasserleitfähigkeit des Bodens bis in eine Tiefe von einem Meter. Bei aktiver Nutzung werden gesättigte Bedingungen unterhalb der Geländeoberkante angenommen. Eine hohe Leitfähigkeit begünstigt hohe Versickerungsraten.",
        'hydraulic_conductivity_2m': "Die hydraulische Leitfähigkeit ist die gesättigte Wasserleitfähigkeit des Bodens bis in eine Tiefe von zwei Metern. Bei aktiver Nutzung werden gesättigte Bedingungen unterhalb der Geländeoberkante angenommen. Eine hohe Leitfähigkeit begünstigt hohe Versickerungsraten.",
    },
    'WeightingsAgricultureForm': {
        'field_capacity': 'Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt Versickerungsmaßnahmen.',
        'hydromorphy': "Die Hydromorphie unterscheidet zwischen grund-, stau- und sickerwasserdominierten landwirtschaftlichen Standorten. Für Versickerungsmaßnahmen sind letztere zu bevorzugen." ,
        'soil_type': "Bewertung der Eignung der vorliegenden Bodenarten landwirtschaftlicher Standorte für Versickerungmaßnahmen." 
    },
    'WeightingsGrasslandForm': {
        'field_capacity': 'Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt Versickerungsmaßnahmen.',
        'hydromorphy':  "Die Hydromorphie unterscheidet zwischen grund-, stau- und sickerwasserdominierten landwirtschaftlichen Standorten. Für Versickerungsmaßnahmen sind letztere zu bevorzugen.",
        'soil_type': "Bewertung der Eignung der vorliegenden Bodenarten landwirtschaftlicher Standorte für Versickerungmaßnahmen." ,
        'soil_water_ratio':  "Bewertung der Sättigungsgrade von Böden auf Graslandstandorten.",
        },
        ### TUB MAR
    'MarWeightingForm': {
            'aquifer_thickness': "Gewichtung der Mächtigkeit des Grundwasserleiters",
            'depth_groundwater': "Gewichtung der Tiefe zum Grundwasserleiter 2",
            'hydraulic_conductivity': "Gewichtung der hydraulischen Leitfähigkeit",
            'land_use': "Gewichtung der Landnutzung",
            'distance_to_source_water': "Gewichtung der Entfernung zum Rohwasser",
            'distance_to_well': "Gewichtung der Entfernung zum Brunnen (m)",
        },
    'SuitabilityForm': {
        'conductivity_10_to_20': None,
        'conductivity_20_to_30': None,
        'conductivity_5_to_10': None,
        'conductivity_gt_30': None,
        'conductivity_lt_5': None,
        'cropland': None,
        'depth_20_to_30': None,
        'depth_30_to_40': None,
        'depth_40_to_50': None,
        'depth_gt_50': None,
        'depth_lt_20': None,
        'distance_1200_to_1500': None,
        'distance_250_to_500': None,
        'distance_500_to_800': None,
        'distance_800_1200': None,
        'distance_gt_1500': None,
        'distance_lt_250': None,
        'forest_closed_coniferous': None,
        'forest_closed_deciduous': None,
        'forest_closed_mixed': None,
        'forest_closed_unknown': None,
        'forest_open_coniferous': None,
        'forest_open_deciduous': None,
        'forest_open_mixed': None,
        'forest_open_unknown': None,
        'herbaceous_vegetation': None,
        'herbaceous_wetland': None,
        'out_of_catchment_gt_5km': None,
        'out_of_catchment_lt_5km': None,
        'permanent_waterbodies': None,
        'shrubs': None,
        'thickness_20_to_30': None,
        'thickness_30_to_40': None,
        'thickness_40_to_60': None,
        'thickness_gt_60': None,
        'thickness_lt_20': None,
        'urban': None,
        'well_catchment': None,
        'zone_1_and_2': None,
        'zone_3': None
      },
      ###Sieker Large Lakes (Oberflächengewässer Filter)
    'SiekerLargeLakeFilter': {
      'area_ha': 'Filter für die Fläche der angezeigten Seen',
      'vol_mio_m3': 'Filter für das Wasservolumen der angezeigten Seen',
      'd_max_m': 'Filter für die maximale Tiefe der angezeigten Seen',
    },
    'SiekerSinkFilter': {
        'volume': 'Setzt die Spanne des Speichervolumens der angezeigten Senken',
      'depth': 'Setzt die Spanne der maximalen Tiefen der angezeigten Senken',
      'avg_depth': 'Setzt die Spanne der durchschnittlichen Tiefen (Volumen pro Fläche) der angezeigten Senken',
      'urbanarea_percent': 'Flächenanteil der Senke, der mit Siedlungsgebieten überlappt',
      'wetlands_percent': 'Flächenanteil der Senke, der mit Feuchtgebieten überlappt',
      'area': 'Setzt die Spanne der Flächen der angezeigten Senken',
      'feasibility': 'Filter für die Einschätzung der Umsetzbarkeit einer Wasserspeicherung in der Senke'
      },
    'GekRetentionFilter': {'costs': 'Filter f\x81r die gesch\x84tzten Umsetzungskosten einer Maánahmentyps',
      'landuse': 'Aktuelle Landnutzung am Standort der Maánahme',
      'priority': 'Priori\x84t der vorgeschlagenen Maánahmen aus dem Gew\x84sserentwicklungskonzept'
      },
    'HistoricalWetlandsFilter': {
        'feasibility': 'Umsetzbarkeit der Wasserspeicherung in der entsprechenden Senke'
      },
      'DrainageNetworkFilter': {
          '':  None,
      },
      'DrainageProbabilityFilterForm': {
          'threshold': 'Schwellenwert für die dargestellte Entwässerungswahrscheinlichkeit'
      },
      
}
