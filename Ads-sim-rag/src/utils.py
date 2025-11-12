import os
import json
from datetime import datetime

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def save_json(data, filename):
    ensure_dir(filename)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def utc_to_str(utc_ts):
    return datetime.utcfromtimestamp(utc_ts).strftime("%Y-%m-%d %H:%M:%S")
