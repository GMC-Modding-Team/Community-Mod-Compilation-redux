import os
import json
import subprocess
import logging


def change_file(json_dir: str, gen_new):
    """Rewrite all json files in json_dir with gen_new.

    :json_dir: Path to directory or file. Should be absolute to avoid path errors.
    :gen_new: Function to apply to each .json file. Should return None if no change."""
    if not os.path.isabs(json_dir):
        logging.warning("Filepath %s is not absolute.", json_dir)

    if os.path.isfile(json_dir):
        modify_file(json_dir, gen_new)

    for root, directories, filenames in os.walk(json_dir, onerror=handle_error):
        for filename in filenames:
            path = os.path.join(root, filename)
            if path.endswith(".json"):
                modify_file(path, gen_new)


def handle_error(error: OSError):
    """Log any OSError raised by os.walk"""
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
            json.dump(new, jf, ensure_ascii=False)
        subprocess.run(["./json_formatter.exe", path])
    else:
        # The average user doesn't care about the files that don't change.
        logging.debug("No change to %s", path)


def load_json(path):
    """Handle errors in json loading.

    Use both print and log to make sure the user is informed."""
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
