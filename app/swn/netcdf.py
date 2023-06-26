import numpy as np
from netCDF4 import Dataset
import os
from pathlib import Path

def write_output_to_netcdfs(row, col, msg_data, npas):
    for data in msg_data:
        results = data.get("results", [])
        for i, npa in enumerate(npas):
            npa[:, row, col] = np.fromiter(map(lambda v: v*100.0, results[i]), dtype="f8")

def open_monica_netcdf(filename):
    PARENT_DIR = Path(__file__).resolve().parent
    nc_file_path = Path.joinpath(PARENT_DIR, 'data', 'monica_net_cdf', filename)
    # open netcdf
    if os.path.exists(nc_file_path):
        print('path exists')
        rootgrp = Dataset(nc_file_path, "r", format="NETCDF4")
        sm1 = rootgrp.variables["sm_sum_0-30"]
        sm2 = rootgrp.variables["sm_sum_30-200"]
        nfc = rootgrp.variables["pnfc_avg_0-30"]
        print('rootgrp')
        print(rootgrp)
        dict_sm_sum = rootgrp.variables
        for key in rootgrp.variables:
            print('key', key)
            print('value: Length', len(rootgrp.variables[key]), '\nValue Type:', type(rootgrp.variables[key]))
       
        rootgrp.close()
    #sm1 3dim np array [0] Tag im Jahr 0-366
    # Tag: [row, col] row: 875 Zeilen col: 643 DE UTM 32N 

