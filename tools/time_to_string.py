#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# They must be in the same folder!
# For Windows:
# Using command prompt type "python time_to_string.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
from base_script import change_file, load_json

logging.basicConfig(filename="time_to_string.log", level=logging.INFO)
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

        # These need no conversion.
        if type(jo.get("time")) == str:
            continue

        # It has to have time.
        if not jo.get("time"):
            continue

        if jo.get("type") == "construction":
            # Convert time to minutes.
            jo["time"] = str(jo["time"]) + " m"
            change = True

        elif jo.get("type") == "recipe":
            # Convert time from turns to seconds, then minutes.
            # Loses the remainder.
            turns = jo["time"]
            turns //= 100
            if turns % 60 == 0:
                turns //= 60
                jo["time"] = str(turns) + " m"
            else:
                jo["time"] = str(turns) + " s"
            change = True

    return json_data if change else None


if __name__ == "__main__":
    json_dir = input("What directory are the json files in? ")
    change_file(json_dir, gen_new)
