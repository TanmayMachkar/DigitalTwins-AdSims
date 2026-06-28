"""
Step 3: Simulate user reactions to a Reddit post using the indexed twin profiles.

Usage:
    python simulate.py --post-id <post_id>
    python simulate.py --post-id 1krk2jt --limit 10   # simulate only first 10 users

Skips users already present in the output CSV.
Requires index.py to have been run first.
"""

import argparse
import csv
import json
import logging
import os

import chromadb
from chromadb.utils import embedding_functions

from src.simulator import simulate_reaction
from src.config import RAW_DIR, EMBEDDING_DIR

os.makedirs("logs", exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--post-id", required=True, help="Reddit post ID (e.g. 1krk2jt)")
parser.add_argument("--limit", type=int, default=None, help="Max number of users to simulate")
args = parser.parse_args()

POST_ID = args.post_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/simulate_{POST_ID}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

OUTPUT_CSV = f"simulation_results_{POST_ID}.csv"
CSV_HEADER = ["username", "predicted_response", "post_url"]

meta_file = os.path.join(RAW_DIR, f"{POST_ID}_post_meta.json")
histories_file = os.path.join(RAW_DIR, f"{POST_ID}_user_histories.json")

if not os.path.isfile(meta_file) or not os.path.isfile(histories_file):
    logger.error(f"Raw data not found for post {POST_ID}. Run collect.py first.")
    exit(1)

with open(meta_file, "r", encoding="utf-8") as f:
    post_info = json.load(f)
with open(histories_file, "r", encoding="utf-8") as f:
    user_histories = json.load(f)

POST_URL = f"https://www.reddit.com/comments/{POST_ID}/"
logger.info(f"Post: {post_info['title']}")
logger.info(f"Total users with history: {len(user_histories)}")

embed_fn = embedding_functions.DefaultEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path=EMBEDDING_DIR)
collection = chroma_client.get_collection(name="user_memory", embedding_function=embed_fn)
logger.info(f"Vector DB loaded. Total vectors: {collection.count()}")

already_done = {}
if os.path.isfile(OUTPUT_CSV):
    with open(OUTPUT_CSV, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            already_done[row["username"]] = row
    logger.info(f"Loaded {len(already_done)} existing results from {OUTPUT_CSV}.")

users = list(user_histories.keys())
if args.limit:
    users = users[:args.limit]
    logger.info(f"Limiting simulation to first {args.limit} users.")

pending = [u for u in users if u not in already_done]
logger.info(f"Users to simulate: {len(pending)} | Skipping already done: {len(users) - len(pending)}")

all_results = dict(already_done)

for username in pending:
    logger.info(f"Simulating: {username}")
    twin_id = f"twin_{username}"

    predicted_response = simulate_reaction(post_info["title"], twin_id, collection)
    logger.info(f"Response for {username}:\n{predicted_response}")

    all_results[username] = {
        "username": username,
        "predicted_response": predicted_response,
        "post_url": POST_URL,
    }

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
    writer.writeheader()
    writer.writerows(all_results.values())

logger.info(f"Saved {len(all_results)} results to {OUTPUT_CSV}.")
