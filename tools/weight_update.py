#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# They must be in the same folder!
# For Windows:
# Using command prompt type "python weight_update.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
from base_script import change_file, load_json

logging.basicConfig(filename="weight_update.log", level=logging.INFO)
logging.info("Started logging.")


def gen_new(path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None
    for jo in json_data:
        # We only want JsonObjects
        if type(jo) is str:
            continue
        # And only if they have weight
        if not jo.get("weight"):
            continue
        # Mapgen uses the wrong type of weight, so we exclude it.
        elif jo.get("type") in ["mapgen", "overmap_terrain", "mod_tileset"]:
            continue
        # We're only looking for integers.
        elif isinstance(jo.get("weight"), int):
            weight = jo["weight"]
            jo["weight"] = str(weight) + " g"
            change = True

    return json_data if change else None


if __name__ == "__main__":
    json_dir = input("What directory are the json files in? ")
    change_file(json_dir, gen_new)
