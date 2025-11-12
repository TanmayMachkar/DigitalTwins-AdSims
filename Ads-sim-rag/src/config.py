import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

DATA_DIR = "data/"
RAW_DIR = os.path.join(DATA_DIR, "raw/")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed/")
EMBEDDING_DIR = os.path.join(DATA_DIR, "embeddings/")
