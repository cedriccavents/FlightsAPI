import datetime
import pandas as pd
import math

def roundup(x):
    return math.ceil(x / 100.0) * 100

def holiday_return_dt(start_date: str, num_nights=10) -> str:
    """ Calculates return date based on number of nights (default=10)
    """
    dt = pd.to_datetime(start_date, format='%Y-%m-%d')
    end_dt = dt + datetime.timedelta(days=num_nights)
    return end_dt.strftime('%Y-%m-%d')

def format_dt(x, months=False):
    try:
        if months:
            dt = pd.to_datetime(
                str(x['month']) + "-" + str(x['year']),
                format="%m-%Y"
            )
        else:
            dt = pd.to_datetime(
                str(x['year']),
                format="%Y"
            )
    except:
        # Exception for end dates -> current date
        dt = datetime.datetime.now()
    return dt

