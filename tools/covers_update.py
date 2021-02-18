#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# They must be in the same folder!
# For Windows:
# Using command prompt type "python covers_update.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
from base_script import change_file, load_json

logging.basicConfig(filename="covers_update.log", level=logging.DEBUG)
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
        # And only if they have coverage
        if not jo.get("covers"):
            continue
        joc = []
        for bodypart in jo["covers"]:
            if bodypart.endswith("_EITHER"):
                bodypart = bodypart[:-7]
                jo["sided"] = True
                bodypart = bodypart + "s"
            if bodypart == "ARMS":
                joc.append("arm_l")
                joc.append("arm_r")
            elif bodypart == "EYES":
                joc.append("eyes")
            elif bodypart in ["FEET", "FOOTS"]:
                joc.append("foot_l")
                joc.append("foot_r")
            elif bodypart == "HANDS":
                joc.append("hand_l")
                joc.append("hand_r")
            elif bodypart == "HEAD":
                joc.append("head")
            elif bodypart == "LEGS":
                joc.append("leg_l")
                joc.append("leg_r")
            elif bodypart == "MOUTH":
                joc.append("mouth")
            elif bodypart == "TORSO":
                joc.append("torso")
            else:
                joc.append(bodypart)
        if jo["covers"] == joc:
            continue
        jo["covers"] = joc
        change = True

    return json_data if change else None


if __name__ == "__main__":
    json_dir = input("What directory are the json files in? ")
    change_file(json_dir, gen_new)
