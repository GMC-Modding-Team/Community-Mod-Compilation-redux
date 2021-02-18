#!/usr/bin/env python3

# Make sure you have python3 installed.
# Ensure that the json_formatter is kept in Tools with this script.
# For Windows:
# Using command prompt type "python name_strings_to_objects.py"
# For Max OS X or Linux:
# Swap any "\\" with "/", then run the script as in windows.

import logging
from base_script import change_file, load_json

logging.basicConfig(filename="price_to_string.log", level=logging.INFO)
logging.info("Started logging.")


def convert_price(jo, key):
    price = jo[key]
    if price == 0:
        jo[key] = "0 cent"
    elif price % 100000 == 0:
        jo[key] = str(price // 100000) + " kUSD"
    elif price % 100 == 0:
        jo[key] = str(price // 100) + " USD"
    else:
        jo[key] = str(price) + " cent"
    return jo


def gen_new(path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None
    for jo in json_data:
        # We only want JsonObjects
        if type(jo) is str:
            continue
        if type(jo.get("price")) is int:
            jo = convert_price(jo, "price")
            change = True

        if type(jo.get("price_postapoc")) is int:
            jo = convert_price(jo, "price_postapoc")
            change = True

    return json_data if change else None


if __name__ == "__main__":
    json_dir = input("What directory are the json files in? ")
    change_file(json_dir, gen_new)
