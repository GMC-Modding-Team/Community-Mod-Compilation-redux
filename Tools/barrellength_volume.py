#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# They must be in the same folder!
# For Windows:
# Using command prompt type "python barrellength_volume.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
from base_script import change_file, load_json

logging.basicConfig(filename="barrellength_volume.log", level=logging.INFO)
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
        if (
            type(jo.get("volume")) != str
            and jo.get("volume")
            and jo.get("type") not in ["sound_effect", "speech"]
        ):
            volume = jo["volume"]
            volume *= 250
            if volume > 10000 and volume % 1000 == 0:
                jo["volume"] = str(volume // 1000) + " L"
            else:
                jo["volume"] = str(volume) + " ml"
            change = True
        if jo.get("barrel_length"):
            if type(jo["barrel_length"]) == int:
                barrel_length = jo["barrel_length"]
                barrel_length *= 250
                jo["barrel_volume"] = str(barrel_length) + " ml"
            elif type(jo["barrel_length"]) == str:
                jo["barrel_volume"] = jo["barrel_length"]
            del jo["barrel_length"]
            change = True

    return json_data if change else None


if __name__ == "__main__":
    json_dir = input("What directory are the json files in? ")
    change_file(json_dir, gen_new)
