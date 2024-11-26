import json
import sys
import os
sys.path.append("/home/niv/dev/where_2_go/")
from external_integrations.gmaps_integration_utils import generate_random_coordinates, get_route_info

from external_integrations.optimization_engine_utils import get_distance_and_duration_from_game_id, \
    get_distance_and_duration_from_game_id_and_compare_with_brute
import logging
from openai import OpenAI
logger = logging.getLogger(__name__)

client = OpenAI()


def get_points_from_json(file_path, route_id, direction_id):
    with open(file_path, 'r') as fid:
        json_dict = json.load(fid)
    route = [r for  r in json_dict['routes'] if r["_id"] == json_dict['route_id'] if r["_id"] == route_id][0]
    waypoints = []
    path = [d for d in route['directions'] if d["id"] == direction_id][0]['path']
    for p in path[1:-1]:
        if p.get("stop", None) is None:
            continue
        waypoints.append({"lat": p["checkPoint"]["lat"], "lng": p["checkPoint"]["lng"], "stop_id": p.get("stop", None)})
    p = path[0]
    origin = [{"lat": p["checkPoint"]["lat"], "lng": p["checkPoint"]["lng"], "stop_id": p.get("stop", None)}]
    p = path[-1]
    destination = [{"lat": p["checkPoint"]["lat"], "lng": p["checkPoint"]["lng"], "stop_id": p.get("stop", None)}]
    return origin, destination, waypoints, path



def generate_path_from_timeplan_json(directory_path, route_id, direction_id, timeplan_name):
    origin, destination, waypoints, path = get_points_from_json(os.path.join(directory_path, timeplan_name),
                                                                route_id, direction_id)
    data = get_route_info(origin, destination, waypoints)
    with open(os.path.join(directory_path, "path.json"), 'w') as fid:
        json.dump({"origin": origin, "destination": destination, "waypoints": waypoints}, fid)
    return origin, destination, waypoints, path, data


def generate_human_understandable_driving_directions_with_gen_ai(directory_path, google_api_json_file):
    instructions_path = os.path.join(directory_path, "instructions.txt")
    assistant = client.beta.assistants.create(
        name="Google direction in human readable format",
        instructions=open(instructions_path, 'r').read(),
        model="gpt-4o",
        temperature=0,
    )

    thread = client.beta.threads.create()

    content = "Here is the json file, please use it to generate the human understandable driving directions\n\n"
    with open(os.path.join(directory_path, google_api_json_file), 'r') as fid:
        content += fid.read()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    run.status

    messages = list(client.beta.threads.messages.list(thread_id=thread.id))
    # for m in messages:
    #     print("*****************************")
    #     print(m.role)
    #     print(m.content)

    directions_text = messages[0].content[0].text.value
    print(directions_text)
    with open(os.path.join(directory_path, "directions.txt"), "w") as fid:
        fid.write(directions_text)
    return directions_text

def generate_sub_file_with_gen_ai(directory_path, video_duration, direction_text):
    instructions_path = os.path.join(directory_path, "instructions2.txt")
    assistant = client.beta.assistants.create(
        name="Google street view video driving instructions synchronization",
        instructions=open(instructions_path, 'r').read(),
        model="gpt-4o",
        temperature=0,
    )

    thread = client.beta.threads.create()


    content = "The video duration is {}sec\nThe directions file content is\n\n{}".format(video_duration, direction_text)

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    run.status

    messages = list(client.beta.threads.messages.list(thread_id=thread.id))
    # for m in messages:
    #     print("*****************************")
    #     print(m.role)
    #     print(m.content)

    sub_file_content = messages[0].content[0].text.value
    sub_file_content = "\n".join(sub_file_content.splitlines()[1:-1])
    with open(os.path.join(directory_path, "directions.sub"), "w") as fid:
        fid.write(sub_file_content)
    return sub_file_content

def _run_single_message(assistant, thread, content):
    logging.debug(f"running message: {content}")
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    if run.status != "completed":
        return False, run.last_error
    messages = list(client.beta.threads.messages.list(thread_id=thread.id))
    content = messages[0].content[0]
    response = content.model_dump()["text"]["value"]
    response = response.strip()
    logging.debug(f"response: {response}")
    return True, response

if __name__ == "__main__":
    directory_path = "utils/gen_ai_utils/resources/"

    # route_id = "erulBUbxMtf"
    # direction_id = "PxylMfV7z7M"
    # timeplan_name = "Hackathon.json"
    # google_api_json_file = "new_york.json"
    # video_duration = 36

    route_id = "UMJyyaX3qNB"
    direction_id = "DzoVDCLY0m_"
    timeplan_name = "gtfs_for_hackathon.json"
    google_api_json_file = "los_angeles.json"
    video_duration = 60

    # origin, destination, waypoints, path, data = generate_path_from_timeplan_json(directory_path, route_id,
    #                                                                               direction_id, timeplan_name)

    # direction_text = generate_human_understandable_driving_directions_with_gen_ai(directory_path, google_api_json_file)

    direction_text = """Here are the driving directions based on the provided JSON data, using the metric system:

1. **Start** at Argyle & Hollywood Blvd, Los Angeles, CA 90028, USA.
   - Head **south** on **Argyle Ave** toward **Hollywood Blvd** for 228 meters.
   
2. **Turn right** onto **Selma Ave**.
   - Continue for 137 meters.

3. **Turn left** at the 1st cross street onto **Vine St**.
   - Your destination will be on the left after 168 meters.
   - **End** at Vine & Sunset Blvd, Los Angeles, CA 90028, USA.

4. **Continue** on **Vine St**.
   - Head **north** for 154 meters.
   - **End** at Vine & Selma Ave, Los Angeles, CA 90028, USA.

5. **Continue** on **Vine St**.
   - Head **north** toward **Selma Ave** for 247 meters.
   - **End** at Vine / Hollywood, Los Angeles, CA 90028, USA.

6. **Continue** on **Vine St**.
   - Head **north** for 356 meters.

7. **Turn right** toward **Franklin Ave**.
   - Continue for 41 meters.

8. **Merge onto** **Franklin Ave**.
   - Continue for 131 meters.
   - **End** at Franklin & Argyle, Los Angeles, CA 90028, USA.

9. **Continue** on **Franklin Ave**.
   - Head **east** toward **Vista Del Mar Ave** for 329 meters.

10. **Turn left** onto **Beachwood Dr**.
    - Your destination will be on the right after 21 meters.
    - **End** at Beachwood & Franklin, Los Angeles, CA 90068, USA.

11. **Continue** on **Beachwood Dr**.
    - Head **north** for 203 meters.
    - **End** at Beachwood & Mid Block, Los Angeles, CA 90068, USA.

12. **Continue** on **Beachwood Dr**.
    - Head **north** toward **Beachwood Terrace** for 316 meters.
    - **End** at Beachwood & Scenic, Los Angeles, CA 90068, USA.

These directions should guide you through the route as described in the JSON data."""

    sub_file_content = generate_sub_file_with_gen_ai(directory_path, video_duration, direction_text)
    print(sub_file_content)
    a = 1







