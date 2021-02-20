#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# They must be in the same folder!
# For Windows:
# Using command prompt type "python material_ammo_update.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
from base_script import change_file, load_json

logging.basicConfig(filename="material_ammo_update.log", level=logging.DEBUG)
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
        if type(jo.get("material")) == str:
            material = jo["material"]
            jo["material"] = [material]
            change = True
        if type(jo.get("ammo")) == str and jo.get("type") == "ammo":
            ammo = jo["ammo"]
            jo["ammo"] = [ammo]
            change = True

    return json_data if change else None


if __name__ == "__main__":
    json_dir = input("What directory are the json files in? ")
    change_file(json_dir, gen_new)
