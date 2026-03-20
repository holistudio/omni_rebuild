import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _ensure_dir(subdir: str):
    path = os.path.join(DATA_DIR, subdir)
    os.makedirs(path, exist_ok=True)
    return path

def save_data(session_id: str, directory: str, data: list[dict]):
    path = _ensure_dir(directory)
    filepath = os.path.join(path, f"{session_id}.json")
    data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "messages": data,
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_data(session_id: str, directory: str, data_key: str):
    filepath = os.path.join(DATA_DIR, directory, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath) as f:
            return json.load(f).get(data_key, [])
    return None