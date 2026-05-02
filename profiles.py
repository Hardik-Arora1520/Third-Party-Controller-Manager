"""
profiles.py — Save and load controller profiles as JSON
"""

import json
import os

PROFILES_DIR = "profiles"


def ensure_profiles_dir():
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)


def save_profile(name, dead_zone, sensitivity, button_map):
    ensure_profiles_dir()
    profile = {
        "name": name,
        "dead_zone": dead_zone,
        "sensitivity": sensitivity,
        "button_map": button_map,
    }
    filepath = os.path.join(PROFILES_DIR, f"{name}.json")
    with open(filepath, "w") as f:
        json.dump(profile, f, indent=4)
    return True


def load_profile(name):
    filepath = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        profile = json.load(f)
    return profile


def list_profiles():
    ensure_profiles_dir()
    files = os.listdir(PROFILES_DIR)
    return [f.replace(".json", "") for f in files if f.endswith(".json")]


def delete_profile(name):
    filepath = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
