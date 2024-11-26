import json
import os
import random
from datetime import timedelta

import requests
# from geopy import Nominatim
import urllib.parse


def get_key():
    "HACK_GOOGLE_API=AIzaSyALpN1vd9bJ15yGs7qQuCv_2Qhb4lDIGjk"
    return os.environ.get("HACK_GOOGLE_API", None)
    return os.environ.get("NIV_PRIVATE_GOOGLE_MAP_API_TOKEN", None)


GOOGLE_API_URL_FORMAT_WALKING = "https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}&mode=walking"

GOOGLE_API_URL_FORMAT_DRIVING = "https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}&mode=driving"

GOOGLE_API_URL_FORMAT_DRIVING_WITH_WAYPOINTS = "https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&waypoints={}&key={}&mode=driving"


GOOGLE_API_URL_FORMAT = GOOGLE_API_URL_FORMAT_DRIVING_WITH_WAYPOINTS

GOOGLE_BROWSER_WALKING_URL_FORMAT = (
    "https://www.google.com/maps/dir/{}/@{},16.18z/?entry=ttu"
)
GOOGLE_CACHE_LOCATION_PATH = "google_cache_path"

if not os.path.exists(GOOGLE_CACHE_LOCATION_PATH):
    os.mkdir(GOOGLE_CACHE_LOCATION_PATH)


def get_durations_from_url(gmaps_url):
    pass


def generate_random_coordinates(city, num_coordinates=10):
    # https://maps.googleapis.com/maps/api/place/textsearch/output?parameters

    # Use the Google Places Nearby Search API to search for places within the city
    safe_city = urllib.parse.quote("random places in " + city)
    print("safe_city", safe_city)
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={safe_city}&key={get_key()}"
    response = requests.get(url)
    data = response.json()

    # Get the list of places
    places = data["results"]
    print(places)
    if len(places) == 0:
        print("no random places found")
        print(data["error_message"])
        return
    # Randomly select a number of places
    random_places = random.sample(places, num_coordinates)

    # Extract the latitude and longitude of each place
    points = [
        (place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"])
        for place in random_places
    ]
    print(points)
    return None, points


def _generate_random_coordinates(city, num_coordinates):
    # Initialize geolocator
    geolocator = Nominatim(user_agent="route-your-way-app")

    # Get city coordinates
    location = geolocator.geocode(city)
    if not location:
        return None

    # create 10 random points in this city

    # Get the bounding box coordinates of the city
    bbox = location.raw["boundingbox"]
    min_lat, max_lat, min_lon, max_lon = map(float, bbox)

    # Generate random coordinates within the bounding box
    coordinates = []
    for _ in range(num_coordinates):
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        coordinates.append((lat, lon))

    if coordinates:
        for i, (lat, lon) in enumerate(coordinates, 1):
            print(f"Coordinate {i}: Latitude {lat}, Longitude {lon}")
    else:
        print("City not found or coordinates not available.", True)

    url = get_url_from_coordinates(coordinates)
    print("{}".format(url))

    return url, coordinates


def get_url_from_coordinates(coordinates):
    coordinate_str = "/".join(
        ["+".join([str(lat), str(lon)]) for (lat, lon) in coordinates]
    )
    last_coordinate = "+".join([str(coordinates[-1][0]), str(coordinates[-1][1])])
    url = GOOGLE_BROWSER_WALKING_URL_FORMAT.format(coordinate_str, last_coordinate)
    return url


def get_route_info(origin, destination, waypoints):
    if not isinstance(origin, str):
        origin = ",".join(map(str, origin))
    if not isinstance(destination, str):
        destination = ",".join(map(str, destination))
    if not isinstance(waypoints, str):
        waypoints = '|'.join(','.join(map(str, waypoint)) for waypoint in waypoints)
    url = GOOGLE_API_URL_FORMAT.format(origin, destination, waypoints, get_key())
    print(f"Fetching data from {url}")
    cache_path = os.path.join(GOOGLE_CACHE_LOCATION_PATH, "{}_{}".format(origin, destination))
    if False and os.path.exists(cache_path):
        try:
            data = json.load(open(cache_path, 'r'))
            print(f"Found data for {origin}, {destination} in cache")
        except Exception as e:
            print("Cached file is corrupted, trying to fetch from API once again")
            print("cache_path: {}, e: {}".format(cache_path, e))
            data = requests.get(url, timeout=1).json()
            print(f"Found data for {origin}, {destination}")
            print(f"Caching data at {cache_path}")
            json.dump(data, open(cache_path, 'w'))
    else:
        data = requests.get(url, timeout=1).json()
        print(f"Found data for {origin}, {destination}")
        print(f"Caching data at {cache_path}")
        json.dump(data, open(cache_path, 'w'))

    if data["status"] == "OK":
        return data
    else:
        print(f"data status {data['status']}", True)
        print(data, True)
        return None


def pairwise(iterable):
    """Generate pairs of consecutive elements from an iterable."""
    a, b = iter(iterable), iter(iterable)
    next(b, None)  # Advance b by one element
    return zip(a, b)


def get_distance_and_duration(coordinates):
    distance = 0
    duration = 0
    for origin, destination in pairwise(coordinates):
        seg_distance, seg_duration = get_route_info(origin, destination)
        if seg_distance is not None and seg_duration is not None:
            distance += seg_distance
            duration += seg_duration
        else:
            print("Failed to retrieve route information.", True)

    return distance / 1000, seconds_to_hh_mm_ss(duration)


def get_coordinates_from_url(url):
    return [
        coordinate.replace(",", "+").split("+")
        for coordinate in url.split("/dir")[1].split("@")[0].split("/")[1:-1]
    ]


def seconds_to_hh_mm_ss(seconds):
    # Create a timedelta object representing the duration
    duration = timedelta(seconds=seconds)
    # Format the duration as HH:MM:SS
    hh_mm_ss = str(duration).split(".")[0]  # Get rid of microseconds
    return hh_mm_ss


def build_all_duration_matrix(coordinates):
    deadhead_index = {}
    for idx, origin in enumerate(coordinates):
        for idy, destination in enumerate(coordinates):
            idx = str(idx)
            idy = str(idy)
            if idx == idy:
                distance = 0
                duration = 0
            else:
                distance, duration = get_route_info(origin, destination)
            if idx not in deadhead_index:
                deadhead_index[idx] = {}
            deadhead_index[idx][idy] = {
                "origin_idx": idx,
                "destination_idx": idy,
                "origin": origin,
                "destination": destination,
                "distance": distance,
                "duration": duration,
            }
    return deadhead_index


def coordinate_to_str(coordinate):
    return ",".join(map(str, coordinate))


def concatenate_coordinates(coordinates):
    result_string = [coordinate_to_str(coordinate) for coordinate in coordinates]
    return "|".join(result_string)


def get_route_info_from_url(new_url):
    new_coordinates = get_coordinates_from_url(new_url)
    return get_distance_and_duration(new_coordinates)
