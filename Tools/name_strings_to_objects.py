#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# For Windows:
# Using command prompt type "python name_strings_to_objects.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
from base_script import change_file, load_json

logging.basicConfig(filename="name_strings_to_objects.log", level=logging.INFO)
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
        if not jo.get("name"):
            continue
        if type(jo["name"]) == dict:
            continue
        if jo.get("type") not in [
            "AMMO",
            "ARMOR",
            "BATTERY",
            "bionic",
            "BIONIC_ITEM",
            "BIONIC_ITEM",
            "BOOK",
            "COMESTIBLE",
            "ENGINE",
            "fault",
            "GENERIC",
            "GUN",
            "GUNMOD",
            "item_action",
            "ITEM_CATEGORY",
            "MAGAZINE",
            "map_extra",
            "martial_art",
            "mission_definition",
            "MONSTER",
            "mutation",
            "npc_class",
            "PET_ARMOR",
            "proficiency",
            "skill",
            "TOOL",
            "TOOL_ARMOR",
            "tool_quality",
            "TOOLMOD",
            "vehicle_part",
            "vehicle_part_category",
            "vitamin",
            "WHEEL",
            "SPELL",
        ]:
            continue
        if jo.get("name_plural"):
            if jo["name"] == jo["name_plural"]:
                name_obj = {"str_sp": jo["name"]}
            else:
                name_obj = {"str": jo["name"], "str_pl": jo["name_plural"]}
            jo["name"] = name_obj
            del jo["name_plural"]
            change = True
        else:
            name_obj = {"str": jo["name"]}
            jo["name"] = name_obj
            change = True

    return json_data if change else None


if __name__ == "__main__":
    json_dir = input("What directory are the json files in? ")
    change_file(json_dir, gen_new)
