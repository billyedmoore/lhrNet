from typing import List, Tuple
import json

from lhrNetUtils import Config

# For create_image_of_state only
from PIL import Image
import numpy as np


def process_state(config: Config, raw_state: dict) -> Tuple[int, List[List[bool]]]:
    """
    Convert a raw_state into an 2d array.

    Args:
        raw_state (dict): A time and list of aircraft states as described
            here https://openskynetwork.github.io/opensky-api/rest.html

    Returns:
        int: Timestamp of the raw_state
        list[list[bool]]: A 2d list of bools where True indicates the presence
            of a plane and False the absence of one
    """

    # our return state
    pixels = [[False] * config.get_x_length() for _ in range(config.get_y_length())]

    y_bin_size = (config.get_lat_offset() * 2) / config.get_y_length()
    x_bin_size = (config.get_long_offset() * 2) / config.get_x_length()

    timestamp = raw_state["time"]

    # Number of x
    # Number of y

    long_min = config.get_heathrow_long() - config.get_long_offset()
    lat_min = config.get_heathrow_lat() - config.get_lat_offset()

    if not raw_state["states"]:
        return timestamp, pixels

    for state in raw_state["states"]:
        long, lat = (state[5], state[6])
        offset_lat, offset_long = (lat - lat_min, long - long_min)

        x = int(offset_long // x_bin_size)
        y = int(offset_lat // y_bin_size)

        # If its within our bounding box
        if x in range(0, config.get_x_length()) and y in range(
            0, config.get_y_length()
        ):
            pixels[y][x] = True
        else:
            print(x, y)

    return timestamp, pixels


def get_raw_states(raw_states_file_path: str) -> List[dict]:
    """
    Get raw states from a file.

    Args:
        raw_states_file_path (str): The path of a file containing the raw_states

    Returns:
        list[dict]: List of raw_states as described here
            https://openskynetwork.github.io/opensky-api/rest.html
    """

    with open(raw_states_file_path, "r") as f:
        states = json.load(f)

    return states


def create_image_of_state(img_out_path: str, state: List[List[bool]]):
    """
    Create an Image at img_out_path for a state using PIL

    Args:
        img_out_path (str): The path to save the image, PIL attempts to infer the filetype
            from the file extension
        state (list[list[bool]]): The state as a 2D list of bools
    """
    arr = np.array(state, dtype=np.uint8) * 255
    img = Image.fromarray(arr, mode="L")
    img.save(img_out_path)


def save_state_as_csv(csv_file_path: str, state: List[List[bool]]):
    """
    Save a state as a csv of 0s and 1s

    Args:
        csv_file_path (str): The path to save the csv
        state (list[list[bool]]): The state as a 2D list of bools
    """
    csv_str = ""
    for row in state:
        row = map(int, row)
        row = map(str, row)

        csv_str += ",".join(row) + "\n"

    with open(csv_file_path, "w") as f:
        f.write(csv_str[:-1])


def main():
    config = Config("config.json")
    states = get_raw_states("raw_data.json")
    for state in states:
        timestamp, pixels = process_state(config, state)
        if any([any(row) for row in pixels]):
            save_state_as_csv(f"data/{timestamp}.csv", pixels)


if __name__ == "__main__":
    main()