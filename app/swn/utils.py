from django.contrib.gis.geoip2 import GeoIP2
import csv 
import json
from datetime import datetime
import pandas as pd
import copy


# helper function to get user's ip location
def get_geolocation(ip):
    g = GeoIP2()

    lat, lon = g.lat_lon(ip)

    return lat, lon

def convert_monica_csv_to_dict(csv_file_path):
    # skipping rows of 0) 'daily' and 2) units, using cols 0)date, 7)LAI, 10) Mois_2
    df = pd.DataFrame(pd.read_csv(csv_file_path, skiprows=[0, 2], usecols=[0,7,10],
                                    sep = ",", header = 0))
    # date is a string!
    monica_dict = df.to_dict(orient='list')
    json_df = json.dumps(monica_dict)

    #date as datetime
    monica_date_dict = copy.deepcopy(monica_dict)
    datelist = [datetime.strptime(date,'%Y-%m-%d') for date in monica_dict['Date']]
    monica_date_dict['Date'] = datelist

    return json_df
    