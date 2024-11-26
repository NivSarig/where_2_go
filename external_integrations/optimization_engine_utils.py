import os
import time
from copy import deepcopy
from random import random

from external_integrations.gmaps_integration_utils import (
    build_all_duration_matrix,
    pairwise,
    get_url_from_coordinates,
    get_distance_and_duration,
)

TSP_PATH = os.environ.get('TSP_PATH', "../external_integrations/optimization_engine/solve_tsp.py")


def get_distance_and_duration_from_game_id(short_coordinates, game_id, location, read_from_cache=True):
    deadhead_index, stops = solve_tsp_from_coordinate_list(
        short_coordinates, game_id, location, read_from_cache
    )

    print(f"tsp_stops:{stops}")

    coordinates = []

    for stop in stops:
        coordinates.append(tuple(deadhead_index[stop][stops[0]]["origin"]))

    url = get_url_from_coordinates(coordinates)
    distance, duration = get_distance_and_duration(coordinates)

    print(f"tsp_distance: {distance}, tsp_duration: {duration}")
    return url, distance, duration, coordinates


def get_distance_and_duration_from_game_id_and_compare_with_brute(
    short_coordinates, game_id, location, read_from_cache
):
    deadhead_index, stops = solve_tsp_from_coordinate_list(
        short_coordinates, game_id, location, read_from_cache
    )

    print(f"tsp_stops:{stops}")

    coordinates = []

    for stop in stops:
        coordinates.append(tuple(deadhead_index[stop][stops[0]]["origin"]))
    distance, duration = get_distance_and_duration(coordinates)

    brute_coordinates = []
    brute_stops = brute_force_solution(deadhead_index, game_id)
    for stop in brute_stops:
        brute_coordinates.append(tuple(deadhead_index[stop][brute_stops[0]]["origin"]))

    url = get_url_from_coordinates(coordinates)
    brute_distance, brute_duration = get_distance_and_duration(brute_coordinates)
    print(f"tsp_stops: {stops}\nbrute_stop: {brute_stops}")
    print(f"brute_distance: {brute_distance}, brute_duration: {brute_duration}")
    print(f"tsp_distance: {distance}, tsp_duration: {duration}")
    assert brute_stops == stops
    return url, distance, duration, coordinates, brute_stops, stops


def solve_tsp_from_coordinate_list(coordinates_list, game_id, location, read_from_cache):

    game_directory = os.path.join(os.getcwd(), game_id)
    if not os.path.exists(game_directory):
        os.mkdir(game_directory)

    deadhead_index = build_all_duration_matrix(coordinates_list)

    return deadhead_index, solve_tsp_for_deadhead_index(
        deepcopy(deadhead_index), game_directory.replace(" ",""), game_id.replace(" ",""),
        location.replace(" ",""), read_from_cache
    )


def solve_tsp_for_deadhead_index(deadhead_index, game_dir, game_id, location, read_from_cache):
    if not os.path.exists(game_dir):
        os.mkdir(game_dir)
    if not os.path.exists(location):
        os.mkdir(location)
    input_file_name = os.path.join(game_dir, "input.tsp")
    output_file_name = os.path.join(game_dir, "output.res")
    location_output_file_name = os.path.join(location, "output.res")

    if read_from_cache and os.path.exists(output_file_name):
        with open(location_output_file_name, "r") as fid:
            print("Returning cached output file: {}".format(location_output_file_name))
            return fid.read().split("\n")

    maximal_deadhead = max(
        set(
            [
                v["duration"]
                for k, inner_dict in deadhead_index.items()
                for ik, v in inner_dict.items()
            ]
        )
    )

    # TSP solves a circular solution (returns to the origin) We will add 2 more auxiliary nodes that will play the
    # role of the first/last node

    maxINF = maximal_deadhead  # 'small INF'
    minMaxINF = 0 * maximal_deadhead  # '0'

    starting_index = str(len(deadhead_index))
    ending_index = str(len(deadhead_index) + 1)
    deadhead_index[starting_index] = deepcopy(deadhead_index[str(0)])
    deadhead_index[ending_index] = deepcopy(deadhead_index[str(0)])
    for source_node in deadhead_index:
        # Add starting and ending index nodes to each dictionary

        deadhead_index[source_node][starting_index] = deepcopy(
            deadhead_index[str(0)][str(0)]
        )
        deadhead_index[source_node][ending_index] = deepcopy(
            deadhead_index[str(0)][str(0)]
        )

    for node in deadhead_index:
        deadhead_index[node][node]["origin_idx"] = node
        deadhead_index[node][node]["destination_idx"] = node
        deadhead_index[node][node]["distance"] = 0
        deadhead_index[node][node]["duration"] = 0

        deadhead_index[starting_index][node]["origin_idx"] = starting_index
        deadhead_index[starting_index][node]["destination_idx"] = node
        deadhead_index[starting_index][node]["distance"] = minMaxINF
        deadhead_index[starting_index][node]["duration"] = minMaxINF
        deadhead_index[starting_index][node]["origin"] = [None, None]
        deadhead_index[starting_index][node]["destination"] = [None, None]

        deadhead_index[ending_index][node]["origin_idx"] = ending_index
        deadhead_index[ending_index][node]["destination_idx"] = node
        deadhead_index[ending_index][node]["distance"] = maxINF
        deadhead_index[ending_index][node]["duration"] = maxINF
        deadhead_index[ending_index][node]["origin"] = [None, None]
        deadhead_index[ending_index][node]["destination"] = [None, None]

        deadhead_index[node][starting_index]["origin_idx"] = node
        deadhead_index[node][starting_index]["destination_idx"] = starting_index
        deadhead_index[node][starting_index]["distance"] = maxINF
        deadhead_index[node][starting_index]["duration"] = maxINF
        deadhead_index[node][starting_index]["origin"] = [None, None]
        deadhead_index[node][starting_index]["destination"] = [None, None]

        deadhead_index[node][ending_index]["origin_idx"] = node
        deadhead_index[node][ending_index]["destination_idx"] = ending_index
        deadhead_index[node][ending_index]["distance"] = minMaxINF
        deadhead_index[node][ending_index]["duration"] = minMaxINF
        deadhead_index[node][ending_index]["origin"] = [None, None]
        deadhead_index[node][ending_index]["destination"] = [None, None]

        deadhead_index[starting_index][ending_index]["origin_idx"] = starting_index
        deadhead_index[starting_index][ending_index]["destination_idx"] = ending_index
        deadhead_index[starting_index][ending_index]["distance"] = maxINF
        deadhead_index[starting_index][ending_index]["duration"] = maxINF
        deadhead_index[starting_index][ending_index]["origin"] = [None, None]
        deadhead_index[starting_index][ending_index]["destination"] = [None, None]

        deadhead_index[ending_index][starting_index]["origin_idx"] = ending_index
        deadhead_index[ending_index][starting_index]["destination_idx"] = starting_index
        deadhead_index[ending_index][starting_index]["distance"] = minMaxINF
        deadhead_index[ending_index][starting_index]["duration"] = minMaxINF
        deadhead_index[ending_index][starting_index]["origin"] = [None, None]
        deadhead_index[ending_index][starting_index]["destination"] = [None, None]

    # Make a symmetric TSP out of the asymmetric problem we have

    sum_of_all_deadheads = sum(
        set(
            [
                v["duration"]
                for k, inner_dict in deadhead_index.items()
                for ik, v in inner_dict.items()
            ]
        )
    )

    INF = str(sum_of_all_deadheads)  # 'large INF'
    mINF = str(0)  # '0'

    dimension = len(deadhead_index)
    tsp_dimension = dimension * 2
    durations = [[INF] * tsp_dimension for __ in range(tsp_dimension)]
    for k1 in range(dimension):
        for k2 in range(dimension):
            if k1 == k2:
                continue
            int_duration12 = str(deadhead_index[str(k1)][str(k2)]["duration"])
            int_duration21 = str(deadhead_index[str(k2)][str(k1)]["duration"])
            durations[int(k1)][int(k2)] = durations[dimension + int(k1)][
                dimension + int(k2)
            ] = INF
            durations[int(k2)][int(k1)] = durations[dimension + int(k2)][
                dimension + int(k1)
            ] = INF

            durations[dimension + int(k1)][int(k2)] = durations[int(k2)][
                dimension + int(k1)
            ] = int_duration12
            durations[dimension + int(k2)][int(k1)] = durations[int(k1)][
                dimension + int(k2)
            ] = int_duration21
            # durations[int(k1)][dimension + int(k2)] = int_duration12
            # durations[dimension + int(k2)][int(k1)] = int_duration21

        durations[int(k1)][int(k1)] = durations[dimension + int(k1)][
            dimension + int(k1)
        ] = "0"
        durations[int(k1)][dimension + int(k1)] = durations[dimension + int(k1)][
            int(k1)
        ] = mINF

    duration_str = []
    for line_idx, duration_line in enumerate(durations):
        duration_str.append(" ".join(duration_line[: line_idx + 1]))
    duration_str = "\n".join(duration_str)
    file_content = """NAME: {}
TYPE: TSP
COMMENT: Location {}
DIMENSION: {}
EDGE_WEIGHT_TYPE: EXPLICIT
EDGE_WEIGHT_FORMAT: LOWER_DIAG_ROW
EDGE_WEIGHT_SECTION
{}
EOF""".format(
        game_id, location or game_id, tsp_dimension, duration_str
    )

    with open(input_file_name, "w") as fid:
        fid.write(file_content)
    print(file_content)

    try:
        os.system(
            "python {} --input {} --output  {}".format(
                TSP_PATH, input_file_name, output_file_name
            )
        )
        print("TSP found a circular solution")
    except Exception as e:
        print("Oh boy TSP failed with error: e: {}".format(e))
    print_full_matrix = True
    if print_full_matrix:
        duration_str = []
        for line_idx, duration_line in enumerate(durations):
            line_str = str(line_idx) + ": "
            for col_idx, duration_item in enumerate(duration_line):
                line_str += f"({str(line_idx)},{col_idx}):{duration_item}, "

            duration_str.append(line_str)
        duration_str = "\n".join(duration_str)
        print(duration_str)
    symmetric_output_file_name = os.path.join(game_dir, "output.res")

    with open(symmetric_output_file_name, "r") as fid:
        # Remove \n and remove any auxiliary index
        asymmetric_output_columns = fid.read().split('\n')
        asymmetric_output_columns = asymmetric_output_columns[:-1][::2]
        if len(set(asymmetric_output_columns)) != dimension:
            raise Exception(f"The {game_id} game in location {location} can not be solved efficiently with our current "
                            f"algorithm Please try a different one.")

        max1_index, max2_index = [i for i, j in sorted(list(enumerate(asymmetric_output_columns)),
                                                      key=lambda x:int(x[1]), reverse=True)[:2]]

        if max2_index < max1_index:
            asymmetric_output_columns = list(
                reversed(
                    list(
                        asymmetric_output_columns[max1_index + 1 :]
                        + asymmetric_output_columns[:max2_index]
                    )
                )
            )
        else:
            asymmetric_output_columns = list(asymmetric_output_columns[max2_index+1:] +
                                             asymmetric_output_columns[:max1_index])

    asymmetric_output_file_name = os.path.join(game_dir, "asym-good_output.res")
    with open(asymmetric_output_file_name, "w") as fid:
        fid.write("\n".join(asymmetric_output_columns))
    with open(location_output_file_name, "w") as fid:
        fid.write("\n".join(asymmetric_output_columns))

    return asymmetric_output_columns


def brute_force_solution(deadhead_index, game_id):

    game_directory = os.path.join(os.getcwd(), game_id)
    output_file_name = os.path.join(game_directory, "brute_output.res")
    all_stop_indices = list(deadhead_index.keys())
    print("Finding a brute force solution over {} stops".format(len(all_stop_indices)))
    import itertools

    # Generate all permutations
    permutations = itertools.permutations(all_stop_indices)
    best_duration = float("inf")
    best_perm = None
    number_of_permutations_checked = 0
    for permutation in permutations:
        number_of_permutations_checked += 1
        perm_duration = 0
        for perm_pair in pairwise(permutation):
            perm_duration += deadhead_index[str(perm_pair[0])][str(perm_pair[1])][
                "duration"
            ]
        if perm_duration < best_duration:
            best_duration = perm_duration
            best_perm = permutation
    print(
        f"Checked {number_of_permutations_checked} permutations for {len(all_stop_indices)} stops"
    )
    indices = list(best_perm)
    with open(output_file_name, "w") as fid:
        fid.write("\n".join(indices))
    return indices


if __name__ == "__main__":
    pass
