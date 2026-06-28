"""
Step 1: Collect Reddit data and build digital twin profiles.

Usage:
    python collect.py --url <reddit_post_url>

Skips data fetching if raw files already exist for the post.
Skips twin profile building if processed profiles already exist.
"""

import argparse
import json
import logging
import os
import praw

from src.reddit_client import fetch_commenters_histories
from src.twin_builder import build_twin_profiles
from src.config import RAW_DIR, PROCESSED_DIR, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/collect.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True, help="Reddit post URL to collect data for")
args = parser.parse_args()

POST_URL = args.url

logger.info(f"Resolving post ID for: {POST_URL}")
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)
post_id = reddit.submission(url=POST_URL).id
logger.info(f"Post ID: {post_id}")

raw_histories_file = os.path.join(RAW_DIR, f"{post_id}_user_histories.json")
raw_meta_file = os.path.join(RAW_DIR, f"{post_id}_post_meta.json")

# --- Stage 1: Fetch Reddit data ---
if os.path.isfile(raw_histories_file) and os.path.isfile(raw_meta_file):
    logger.info(f"Raw data already exists for post {post_id}. Loading from disk.")
    with open(raw_histories_file, "r", encoding="utf-8") as f:
        user_histories = json.load(f)
    with open(raw_meta_file, "r", encoding="utf-8") as f:
        post_info = json.load(f)
else:
    logger.info("Fetching user histories from Reddit...")
    user_histories, post_info = fetch_commenters_histories(POST_URL)
    logger.info(f"Fetched {len(user_histories)} user histories.")

# --- Stage 2: Build twin profiles ---
os.makedirs(PROCESSED_DIR, exist_ok=True)
existing_profiles = {f.replace(".json", "") for f in os.listdir(PROCESSED_DIR) if f.endswith(".json")}
new_users = [u for u in user_histories if u not in existing_profiles]

if not new_users:
    logger.info(f"All {len(user_histories)} twin profiles already exist. Skipping.")
else:
    logger.info(f"Building twin profiles for {len(new_users)} new users ({len(existing_profiles)} already exist)...")
    build_twin_profiles(raw_histories_file)
    logger.info("Twin profiles built.")

total_profiles = len(os.listdir(PROCESSED_DIR))
logger.info(f"Done. Post ID: {post_id} | Users collected: {len(user_histories)} | Profiles in {PROCESSED_DIR}: {total_profiles}")
