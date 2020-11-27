import json 
import requests
from pprint import pprint
import numpy as np

# Useful URLs (you need to add the appropriate parameters for your requests)
MAPQUEST_BASE_URL = "http://www.mapquestapi.com/geocoding/v1/address"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"

# Your API KEYS (you need to use your own keys - very long random characters)
MAPQUEST_API_KEY = "auSa1xsiSJl3l1TCt5Ci17FalaRHqXGF"
MBTA_API_KEY = "fd5181087ae743e284ccc86652d81e21"


# A little bit of scaffolding if you want to use it

def get_json(url):
    """
    Given a properly formatted URL for a JSON web API request, return
    a Python dict object containing the response to that request.
    """
    response = requests.get(url)

    return response.json()


def get_lat_long(place_name):
    """
    Given a place name or address, return a (latitude, longitude) tuple
    with the coordinates of the given place.
    See https://developer.mapquest.com/documentation/geocoding-api/address/get/
    for Mapquest Geocoding  API URL formatting requirements.
    """
    js = get_json(f"{MAPQUEST_BASE_URL}?key={MAPQUEST_API_KEY}&location={place_name}")

    return tuple([v for v in js['results'][0]['locations'][0]['latLng'].values()])


def get_nearest_station(latitude, longitude, station_type=None):
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible)
    tuple for the nearest MBTA station to the given coordinates.
    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL
    formatting requirements for the 'GET /stops' API. 

    Optional: Provide station_type to filter by station type. Valid options are:

    0 - Tram, Streetcar, Light rail. Any light rail or street level system within a metropolitan area.
    1 - Subway, Metro. Any underground rail system within a metropolitan area.
    2 - Rail. Used for intercity or long-distance travel.
    3 - Bus. Used for short- and long-distance bus routes.
    4 - Ferry. Used for short- and long-distance boat service.
    """

    # Convert str position to floats
    pos = [float(i) for i in (latitude, longitude)]

    # Construct//Execute API call
    url = f"{MBTA_BASE_URL}?latitude={pos[0]}?longitude={pos[1]}?radius=0.01?route_type={station_type}?api_key={MBTA_API_KEY}?limit=300?format=json"

    stations = get_json(url)['data']

    if station_type != None:
        stations = [s for s in stations if str(s['attributes']['vehicle_type']) == str(station_type)]

    # Functions to extract lat/long tuples and calculate distance to home base
    def process_station(s):
        """Given s, a station in the JSON provided by get_json, computes the euclidean distance 
        between the station and your provided location"""

        # Euclidean distance/l2 norm without the sqrt for efficiency since it's monotonic
        l2 = lambda x: sum([(s - p)**2 for s, p in zip(x, pos)])

        try:
            ll = (float(s['attributes']['latitude']), float(s['attributes']['longitude']))
            return l2(ll)

        except Exception as e:
            # If mbta API doesn't have station location, replace with large distance

            return 9999999


    station_distances = np.asarray([process_station(s) for s in stations])
    closest = stations[np.argmin(station_distances)]

    return [closest['attributes']['name'], closest['attributes']['wheelchair_boarding']]


def find_stop_near(place_name, station_type=None):
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.
    0	No Information
    1	Accessible (if trip is wheelchair accessible)
    2	Inaccessible
    """
    wheelchair_map = {0: "did not provide accessibility information",
                      1: "is Wheelchair Accessible",
                      2: "is Wheelchair Inaccessible"}

    la, lo = get_lat_long(place_name)
    ns = get_nearest_station(la, lo, station_type)
    ns[1] = wheelchair_map[ns[1]]

    return ns


def main():
    """
    You can test all the functions here
    """
    print(find_stop_near("Fenway Baseball Park Boston"))


if __name__ == '__main__':
    main()
