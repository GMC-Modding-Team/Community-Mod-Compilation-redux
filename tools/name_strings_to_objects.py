#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# For Windows:
# Using command prompt type "python name_strings_to_objects.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
import json
import os

logging.basicConfig(filename="name_strings_to_objects.log", level=logging.INFO)
logging.info("Started logging.")


def change_file(json_dir: str, gen_new):
    """Rewrite all json files in json_dir with gen_new.

    :json_dir: Path to directory or file. Should be absolute to avoid path errors.
    :gen_new: Function to apply to each .json file. Should return None if no change.
    """
    if not os.path.isabs(json_dir):
        logging.warning("Filepath %s is not absolute.", json_dir)

    if os.path.isfile(json_dir):
        modify_file(json_dir, gen_new)

    for root, _, filenames in os.walk(json_dir, onerror=handle_error):
        for filename in filenames:
            path = os.path.join(root, filename)
            if path.endswith(".json"):
                modify_file(path, gen_new)


def handle_error(error: OSError):
    """Log any OSError raised by os.walk."""
    try:
        raise error
    except error:
        logging.exception("OSError raised in os.walk")


def modify_file(path, gen_new):
    """Call gen_new on json_file."""
    new = gen_new(path)
    if new is not None:
        logging.info("Modified file %s", path)
        with open(path, "w", encoding="utf-8") as jf:
            json.dump(new, jf, ensure_ascii=False, indent=2)
            jf.write("\n")
    else:
        # The average user doesn't care about the files that don't change.
        logging.debug("No change to %s", path)


def load_json(path):
    """Handle errors in json loading.

    Use both print and log to make sure the user is informed.
    """
    with open(path, "r", encoding="utf-8") as json_file:
        try:
            json_data = json.load(json_file)
        except UnicodeDecodeError:
            print(f"UnicodeDecodeError in {path}")
            logging.error("UnicodeDecodeError in %s", path)
            return None
        except json.decoder.JSONDecodeError:
            print("JSONDecodeError in {0}".format(path))
            logging.error("JSONDecodeError in %s", path)
            return None
    return json_data


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
