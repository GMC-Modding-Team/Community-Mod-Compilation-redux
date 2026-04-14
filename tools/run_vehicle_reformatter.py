"""Run vehicle reformatter multiple times."""

import os

for root, directories, filenames in os.walk("..\\data"):
    for filename in filenames:
        path = os.path.join(root, filename)
        if path.endswith("vehicles.json"):
            os.system("python vehicle_reformatter.py {0}".format(path))
            os.system(".\\format\json_formatter.exe {0}".format(path))
