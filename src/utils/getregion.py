from geopy.geocoders import Nominatim
import pandas as pd
import pathlib
import os

# Relative paths
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('../data').resolve()

def getregion(plz):
    """
    Search test reference year location for given postal code. 
    
    Parameters
    ----------
    plz (postal code)
    
    Returns
    -------
    weatherID (str with climate zone)
    """
    geolocator=Nominatim(user_agent="Hauke", timeout=10)
    location=geolocator.geocode(str(plz)+ ', Germany')
    
    # read weather zones
    wzones = pd.read_csv(DATA_PATH.joinpath('locations/locations.csv'),index_col=0,)
    
    # get distance to all reference weather station points
    dist = ((wzones["Lat"] - location.latitude) ** 2 + (wzones["Lng"] - location.longitude) ** 2) ** 0.5

    # if distance to next reference position is to high.
    if min(dist) > 5:
        raise NotImplementedError(
            "The weather data is only imlemented" + " for for Germany at the moment"
        )

    # get the data from the one with the minimal distance
    loc_w = wzones.loc[dist.idxmin(), :]


    return (loc_w["Climate Zone"])