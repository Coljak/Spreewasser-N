import requests
from datetime import datetime, date
from pathlib import Path
import xarray as xr
import numpy as np
import os
from django.core.cache import cache
from dateutil.relativedelta import relativedelta


def model_germany_forecast():
    
