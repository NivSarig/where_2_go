game_dict = {}
from utils import generate_random_string
from fastapi import BackgroundTasks, HTTPException
import sys, os

sys.path.append(os.getcwd() + "/..")

from external_integrations.optimization_engine_utils import (
    get_distance_and_duration_from_game_id,
)
from external_integrations.gmaps_integration_utils import (
    generate_random_coordinates,
    get_distance_and_duration,
)
from locations import locations


def get_game(game_id):
    # throw exception if game_id doesn't exist
    if game_id not in game_dict:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_dict[game_id]


def create_game(location, code, random, background_tasks: BackgroundTasks):

    new_game_id = code or generate_random_string()
    print("creating game", new_game_id)
    if random:
        _, coordinates = generate_random_coordinates(location, 9)
    else:
        if location not in locations:
            raise HTTPException(status_code=400, detail="Location doesn't exists")
        coordinates = locations[location]

    game_dict[new_game_id] = {
        "location": {"name": location, "coordinates": coordinates},
        "game_id": new_game_id,
        "contestants": {},
        "status": "running",
    }
    if background_tasks is not None:
        background_tasks.add_task(solve, new_game_id, location, coordinates)

    return get_game(new_game_id)


def solve(game_id, location, coordinates):

    url, distance, duration, coordinates_solution = (
        get_distance_and_duration_from_game_id(coordinates, game_id, location)
    )
    print(
        "url: {}, distance: {}, duration: {}, game_id: {}".format(
            url, distance, duration, game_id
        )
    )
    game_dict[game_id]["solution"] = {
        "url": url,
        "distance": distance,
        "duration": duration,
        "coordinates": coordinates_solution,
    }


def verify_existing_name(game_id, name):
    if name not in get_game(game_id)["contestants"]:
        raise HTTPException(status_code=400, detail="Contestant doesn't exists")


def verify_unique_name(game_id, name):
    if name in get_game(game_id)["contestants"]:
        raise HTTPException(
            status_code=400, detail="Contestant already exists (name is taken)"
        )


def add_contestant(game_id, name):
    verify_unique_name(game_id, name)

    game_dict[game_id]["contestants"][name] = {"name": name}
    return get_game(game_id)


def add_submit(game_id, name, indexes):
    curr_game = get_game(game_id)
    verify_existing_name(game_id, name)
    try:
        coordinates = [curr_game["location"]["coordinates"][i] for i in indexes]
        distance, duration = get_distance_and_duration(coordinates)
    except Exception as e:
        curr_game["contestants"][name]["status"] = "failed"
        curr_game["contestants"][name]["message"] = repr(e)

    curr_game["contestants"][name]["duration"] = duration
    curr_game["contestants"][name]["distance"] = distance
    curr_game["contestants"][name]["coordinates"] = coordinates
    curr_game["contestants"][name]["status"] = "done"


create_game("Tel Aviv", "TEST", None, None)
