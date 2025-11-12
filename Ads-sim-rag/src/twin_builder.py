import json
import os
from src.utils import save_json
from src.config import PROCESSED_DIR

def build_twin_profiles(histories_file):
    """Create time-filtered twin profiles (no post timestamp stored)."""
    with open(histories_file, "r", encoding="utf-8") as f:
        user_histories = json.load(f)

    for username, comments in user_histories.items():
        twin = {
            "twin_id": f"twin_{username}",
            "num_comments": len(comments),
            "source_comments": [c["body"] for c in comments],
            "summary": f"{username}: {len(comments)} historical comments before target post."
        }
        save_json(twin, f"{PROCESSED_DIR}{username}.json")
