"""
Step 2: Build the ChromaDB vector database from twin profiles.

Usage:
    python index.py

Skips users that are already indexed. Safe to re-run after adding new profiles.
"""

import json
import logging
import os

import chromadb
from chromadb.utils import embedding_functions

from src.config import EMBEDDING_DIR, PROCESSED_DIR

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/index.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

embed_fn = embedding_functions.DefaultEmbeddingFunction()

os.makedirs(EMBEDDING_DIR, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=EMBEDDING_DIR)

collection = chroma_client.get_or_create_collection(
    name="user_memory",
    embedding_function=embed_fn,
    metadata={"description": "Reddit twin memory DB"}
)

existing_ids = set(collection.get()["ids"])
logger.info(f"Existing vectors in DB: {len(existing_ids)}")

profiles = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".json")]
logger.info(f"Found {len(profiles)} twin profiles in {PROCESSED_DIR}")

skipped, indexed = 0, 0

for file in profiles:
    path = os.path.join(PROCESSED_DIR, file)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        twin_id = data["twin_id"]

        if f"{twin_id}_0" in existing_ids:
            logger.info(f"[SKIP] {twin_id} already indexed.")
            skipped += 1
            continue

        logger.info(f"Indexing {twin_id} ({len(data['source_comments'])} comments)...")
        for i, text in enumerate(data["source_comments"]):
            collection.add(
                ids=[f"{twin_id}_{i}"],
                documents=[text],
                metadatas={"user": twin_id}
            )
        indexed += 1
        logger.info(f"Indexed {twin_id} successfully.")

    except json.JSONDecodeError:
        logger.warning(f"Skipping {file}: invalid JSON.")
    except Exception as e:
        logger.error(f"Could not process {file}: {e}")

logger.info(f"Done. Indexed: {indexed} | Skipped (already indexed): {skipped} | Total vectors in DB: {collection.count()}")
