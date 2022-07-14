from geopy.geocoders import Nominatim
import pandas as pd
import os
def getregion(plz):
    """
    Gets the test reference year location 
    Parameters
    ----------
    plz
    Returns
    -------
    weatherID (str with climate zone)
    """
    geolocator=Nominatim(user_agent="Hauke", timeout=10)
    location=geolocator.geocode(str(plz)+ ', Germany')
    # read weather zones
    print(os.getcwd())
    wzones = pd.read_csv(os.getcwd()+"/functions/T_zones_Ger_final.csv",
        index_col=0,)
    # get distance to all reference weather station points
    dist = ((wzones["Lat"] - location.latitude) ** 2 + (wzones["Lng"] - location.longitude) ** 2) ** 0.5

    # if distance to next reference position is to high.
    if min(dist) > 5:
        raise NotImplementedError(
            "The weather data is at the moment" + " only implemented for Germany"
        )

    # get the data from the one with the minimal distance
    loc_w = wzones.loc[dist.idxmin(), :]


    return (loc_w["Climate Zone"])